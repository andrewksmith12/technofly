# imports all needed modues to the python script
import simple_salesforce
from google.cloud import error_reporting
import creds
import requests
from flask import Flask, request, Response
import json
from simple_salesforce import Salesforce, format_soql
from threading import Thread
TEST_EVENT_URL = "https://www.eventbriteapi.com/v3/events/151257855317/"

EB_API_KEY = creds.EB_API_KEY

# Eventbrite API Authentication Imports
BASE_URL = 'https://www.eventbriteapi.com/v3/'
AUTH_HEADER_EB = {
    'Authorization': 'Bearer {token}'.format(token=EB_API_KEY)
}

# Returns the authenticated salesforce object we'll use to query, create, and update salesforce objects.
def getSalesforce():
    if creds.SF_OPERATING_MODE == "test":
        sf = Salesforce(instance=creds.SF_SANDBOX_URL, username=creds.SF_SANDBOX_USERNAME, password=creds.SF_SANDBOX_PASSWORD, security_token=creds.SF_SANDBOX_SECURITY_TOKEN, domain="test")
    elif creds.SF_OPERATING_MODE == "login":
        sf = Salesforce(instance=creds.SF_PROD_URL, username=creds.SF_USERNAME, password=creds.SF_PASSWORD, security_token=creds.SF_PROD_SECURITY_TOKEN, domain="login")
    else:
        print("Invalid Login Domain. Check/Update creds.py!")
    return sf


# Creates a salesforce account(primary affiliation or a company) given the data from eventbrite.
def createNewAccount(sf, attendee):
    result = ""
    try:
        result = sf.Account.create(
            {'Name': attendee['profile']['company']})
        newAccountID = result['id']
        print("Created new Account for "+attendee['profile']['company'])
    except simple_salesforce.exceptions.SalesforceMalformedRequest as e:
        print(e)
    return newAccountID


# Creates a salesforce contact (person who booked) given the data from eventbrite.
def createNewContact(sf, attendee, accountID):
    result = sf.Contact.create(
        {'Email': attendee['profile']['email'],
         'FirstName': attendee['profile']['first_name'],
         'LastName': attendee['profile']['last_name'],
         'Title': attendee['profile']['job_title'],
         'npsp__Primary_Affiliation__c': accountID})
    newContactID = result['id']
    print("Created new contact for "+attendee['profile']['first_name']+" with sfID "+newContactID)
    return newContactID


# Creates a salesforce campaign member (attendee) given the data from eventbrite.
def createCampaignMember(sf, attendee, campaignID, contactID):
    # sets the question answers to blank
    pocAnswer = ""
    raceAnswer = ""
    raceFreeResponse = ""
    otherQuestions = ""
    howDidYouHearAboutUs = ""

    # if there is any questions that are answered, the blank is replaced with the response from eventbrite
    try:
        for question in attendee['answers']:
            if "black, indigenous, and/or a person of color" in question['question'].lower():
                pocAnswer = question['answer']
            elif "what is your race?" in question['question'].lower():
                raceAnswer = question['answer']
            elif "please describe." == question['question'].lower():
                raceFreeResponse = question['answer']
            elif "how did you hear about this event?" in question['question'].lower():
                howDidYouHearAboutUs = question['answer']
            else:
                otherQuestions = otherQuestions+str(question['question'])+": "+str(question['answer'])+"\n"
    except Exception as e:
        print(e)
        print("Failed to parse questions, may be blank or missing, skipping...")

    try:
        response = sf.CampaignMember.create(
            {'CampaignId': campaignID,
             'ContactId': contactID,
             'EventbriteSync__EventbriteId__c': attendee['id'],
             'Eventbrite_Attendee_ID__c': attendee['id'],
             'Eventbrite_Fee__c': attendee['costs']['eventbrite_fee']['major_value'],
             'Payment_Processing_Fee__c': attendee['costs']['payment_fee']['major_value'],
             'Total_Paid__c': attendee['costs']['base_price']['major_value'],
             'Ticket_Type__c': attendee['ticket_class_name'],
             'Status': attendee['status'],
             'Attendee_Status__c': 'Attending',
             'Identifies_as_BIPOC__c': pocAnswer.replace(" | ", ";"),
             'Race__c': raceAnswer,
             'Race_self_describe__c': raceFreeResponse,
             'How_did_you_hear_about_this_event__c': howDidYouHearAboutUs,
             'Comments__c': otherQuestions})
        print("Created campaign member for "+attendee['profile']['first_name']+" successfully.")
    except Exception as e:
        print(e)
        print("Member may already exist, continuing process...")
        pass


# Creates a salesforce opportunity (financial data) given the data from eventbrite.
def createOpportunity(sf, attendee, contactID, accountID, campaignID, api_url):
    r = requests.get(api_url, headers=AUTH_HEADER_EB, params={"expand": ["category", "promotional_code"]})
    order = r.json()
    buyerQuery = sf.query(format_soql("SELECT Id, Email, npsp__Primary_Affiliation__c, Primary_Affiliation_text__c FROM Contact WHERE Email = '{buyerEmail}'".format(buyerEmail=order['email'].strip().replace('"', '\\"').replace("'", "\\'"))))
    # if salesforce returns one primary affiliation for the attendee, it will select the first primary affiliation returned
    if buyerQuery['totalSize'] == 1:
        buyerID = buyerQuery['records'][0]['Id']
        sf.Contact.update(buyerID, {
            'FirstName': order['first_name'],
            'LastName': order['last_name'],
        })
    # if not, it will create a new contact
    else:
        createResponse = sf.Contact.create({
            'FirstName': order['first_name'],
            'LastName': order['last_name'],
            'Email': order['email']
        })
        buyerID = createResponse['id']
    if "promotional_code" in attendee.keys():
        sf.Opportunity.create({'AccountId': accountID, 'npsp__Primary_Contact__c': contactID, 'EventbriteSync__Buyer__c': buyerID, 'amount': attendee['costs']['gross']['major_value'], 'StageName': 'posted', 'CloseDate': attendee['created'], 'CampaignId': campaignID, 'Order_Number__c': attendee['order_id'], 'Ticket_Type__c': attendee['ticket_class_name'], 'RecordTypeId': '012f4000000JdASAA0', 'Name': 'tempName', 'Coupon_Code__c': attendee['promotional_code']['code']})  # Name is by Salesforce when processed by NPSP
    else:
        sf.Opportunity.create({'AccountId': accountID, 'npsp__Primary_Contact__c': contactID, 'EventbriteSync__Buyer__c': buyerID, 'amount': attendee['costs']['gross']['major_value'], 'StageName': 'posted', 'CloseDate': attendee['created'], 'CampaignId': campaignID, 'Order_Number__c': attendee['order_id'], 'Ticket_Type__c': attendee['ticket_class_name'], 'RecordTypeId': '012f4000000JdASAA0', 'Name': 'tempName'})  # Name is by Salesforce when processed by NPSP
    print("Opportunity created for "+attendee['profile']['first_name'])


# Updates a salesforce contact (person who booked) given the data from eventbrite.
def updateContactNormal(sf, attendee, contactID, accountID):
    sf.Contact.update(contactID,
                      {'FirstName': attendee['profile']['first_name'],
                       'LastName': attendee['profile']['last_name'],
                       'Email': attendee['profile']['email'],
                       'Title': attendee['profile']['job_title'],
                       'npsp__Primary_Affiliation__c': accountID})
    print("Contact updated for "+attendee['profile']['first_name'])


# Creates a salesforce event given the data from eventbrite.
def createEvent(api_url):
    sf = getSalesforce()
    event = requests.get(api_url, headers=AUTH_HEADER_EB, params={"expand": "category", "expand": "promotional_code", "expand": "promo_code"})
    eventData = event.json()
    sf_respond = sf.Campaign.create(
        {'Name': eventData['name']['text'],
         'Event_URL__c': eventData['url'],
         'StartDate': eventData['start']['local'],
         'EndDate': eventData['end']['local'],
         'Type': 'Training Workshop, Small (default)',
         'Status': 'Open',
         'IsActive': True,
         'Description': eventData['description']['text'],
         'EventbriteSync__EventbriteId__c': eventData['id'],
         'RecordTypeId': '012f4000000JcuJAAS'})
    print('Event \"'+eventData['name']['text']+'\" created.')
    print(sf_respond)
    return sf_respond['id']

# Runs through a decision tree based on if the information is available on salesforce and either creates or updates information given the data from eventbrite.
def processOrder(api_url):
    sf = getSalesforce()
    r = requests.get(api_url+"/attendees", headers=AUTH_HEADER_EB, params={"expand": ["category", "promotional_code"]})
    attendees = r.json()
    print("Raw attendees data: ")
    print(attendees)
    for attendee in attendees['attendees']:
        sfCampaign = sf.query(format_soql("SELECT Id FROM Campaign WHERE EventbriteSync__EventbriteId__c = '{ebEventID}'".format(ebEventID=attendee['event_id'])))
        campaignID = sfCampaign['records'][0]['Id']
        print("Checking for an email match for "+attendee['profile']['name'])
        # Search SF for contact with attendee email
        queryResult = sf.query("SELECT Id, Email, npsp__Primary_Affiliation__c, Primary_Affiliation_text__c FROM Contact WHERE Email = '{attendeeEmail}'".format(attendeeEmail=attendee['profile']['email'].strip().replace('"', '\\"').replace("'", "\\'")))
        # Check for edge case: Facebook Registration / Company Not Collected.
        if 'company' not in attendee['profile'].keys():
            print("Company Name missing from record! Processing alternatively...")
            if queryResult['totalSize'] >= 1:
                print("NO COMPANY- Email match found, updating contact FName/LName, making campaign member, making opportunity")
                accountID = queryResult['records'][0]['npsp__Primary_Affiliation__c']
                contactID = queryResult['records'][0]['Id']
                sf.Contact.update(contactID, {
                    'FirstName': attendee['profile']['first_name'],
                    'LastName': attendee['profile']['last_name'],
                })
                createCampaignMember(sf, attendee, campaignID, contactID)
                createOpportunity(sf, attendee, contactID, accountID, campaignID, api_url)
            elif queryResult['totalSize'] == 0:
                print("NO COMPANY- Contact not found in salesforce. Creating new contact, campaign member, opportunity and proceeding with limited information...")
                result = sf.Contact.create(
                    {'Email': attendee['profile']['email'],
                     'FirstName': attendee['profile']['first_name'],
                     'LastName': attendee['profile']['last_name']})
                newContactID = result['id']
                createCampaignMember(sf, attendee, campaignID, newContactID)
                createOpportunity(sf, attendee, newContactID, "", campaignID, api_url)

        # If contact with an email IS found.
        elif queryResult['totalSize'] >= 1:
            print("Email match(es) found!")
            contactID = queryResult['records'][0]['Id']
            print("Checking if primary affiliation is an exact match....")
            # If Primary Affilation matches: Update contact FName/LName/Title, add campaign member.
            if queryResult['records'][0]['Primary_Affiliation_text__c'] == None:
                queryResult['records'][0]['Primary_Affiliation_text__c'] = ""
            elif queryResult['records'][0]['Primary_Affiliation_text__c'].lower() == attendee['profile']['company'].lower():
                accountID = queryResult['records'][0]['npsp__Primary_Affiliation__c']
                print("Matches Primary Affiliation! Updating records...")
                updateContactNormal(sf, attendee, contactID, accountID)
                createCampaignMember(sf, attendee, campaignID, contactID)
                createOpportunity(sf, attendee, contactID, accountID, campaignID, api_url)
                print("Done!")
            # If primary affiliation doesn't match
            else:
                print("Primary Affiliation does not match")
                accountQuery = sf.query(format_soql("SELECT Id, Name from Account WHERE Name LIKE '{ebOrg}'".format(ebOrg=attendee['profile']['company'].strip().replace('"', '\\"').replace("'", "\\'"))))
                # If primary affiliaiton doesn't match, but it exists in salesforce update the contact and create the campaign member
                if accountQuery['totalSize'] >= 1:
                    print("Matching account found. Starting update contact, create campaign member, create opportunity.")
                    accountID = accountQuery['records'][0]['Id']
                    updateContactNormal(sf, attendee, contactID, accountID)
                    createCampaignMember(sf, attendee, campaignID, queryResult['records'][0]['Id'])
                    createOpportunity(sf, attendee, contactID, accountID, campaignID, api_url)
                    print("Done!")
                # If primary affiliation doesn't match and doesn't exist in salesforce, create new account, update the contact, and create campaign member
                else:
                    print("No matching account found. Starting Create Account, Contact, CampaignMember")
                    newAccountID = createNewAccount(sf, attendee)
                    updateContactNormal(sf, attendee, contactID, newAccountID)
                    createCampaignMember(sf, attendee, campaignID, contactID)
                    createOpportunity(sf, attendee, contactID, newAccountID, campaignID, api_url)
                    print("Done!")

        # If contact with email is not found
        elif queryResult['totalSize'] == 0:
            print("Email match failed. Checking if Account exists in Salesforce...")
            accountQueryResult = sf.query(format_soql(("SELECT Id, Name from Account WHERE Name LIKE '{ebOrg}'".format(ebOrg=attendee['profile']['company'].strip().replace('"', '\\"').replace("'", "\\'")))))
            # If the account doesn't exist in Salesforce, make the account, contact, campaign record
            if accountQueryResult['totalSize'] == 0:
                print("No matching Account. Starting create Account, Contact, and Campaign Member")
                newAccountID = createNewAccount(sf, attendee)
                newContactID = createNewContact(sf, attendee, newAccountID)
                createCampaignMember(sf, attendee, campaignID, newContactID)
                createOpportunity(sf, attendee, newContactID, newAccountID, campaignID, api_url)
                print("Done!")
                # Create new Account, new Contact, and the event affiliation.
            # if the account does exist, search by name
            else:
                print("Matching Account Found, searching by name...")
                accountID = accountQueryResult['records'][0]['Id']
                personQueryResult = sf.query(format_soql("SELECT Id, Name, Primary_Affiliation_text__c FROM Contact WHERE Name='{ebName}' AND Primary_Affiliation_text__c LIKE '{ebCompany}'".format(ebName=attendee['profile']['name'].strip().replace('"', '\\"').replace("'", "\\'"), ebCompany=attendee['profile']['company'].strip().replace('"', '\\"').replace("'", "\\'"))))
                # If there's an exact name match, update the contact, create the campaign member.
                if personQueryResult['totalSize'] == 1:
                    print("Match found by Name and Company. Starting update contact, create campaign member, create opportunity.")
                    contactID = personQueryResult['records'][0]['Id']
                    updateContactNormal(sf, attendee, contactID, accountID)
                    createCampaignMember(sf, attendee, campaignID, contactID)
                    createOpportunity(sf, attendee, contactID, accountID, campaignID, api_url)
                    print("Done!")
                else:
                    print("Person not found. Starting create new contact, campaign member, opportunity.")
                    # SF create new contact in account matched in "accountQueryResult"
                    newContactID = createNewContact(sf, attendee, accountID)
                    # SF create new Campaign Member record with new ContactID and the Campaign ID from sfCampaign.
                    createCampaignMember(sf, attendee, campaignID, newContactID)
                    createOpportunity(sf, attendee, newContactID, accountID, campaignID, api_url)
                    print("Done!")


# When an attendee is checked in on eventbrite, the attendee is checked in on salesforce
def processCheckin(api_url):
    sf = getSalesforce()
    # Find CM record in SF, mark as checked in.
    registration = requests.get(api_url, headers=AUTH_HEADER_EB, params={"expand": "category", "expand": "promotional_code", "expand": "promo_code"})
    registration = registration.json()
    print("Processing checkin...")
    print(registration)
    campaignMemberQuery = sf.query(format_soql("SELECT Id FROM CampaignMember WHERE Eventbrite_Attendee_ID__c = '{attendeeID}'".format(attendeeID=registration['id'].strip().replace('"', '\\"').replace("'", "\\'"))))
    if campaignMemberQuery['totalSize'] >= 1:
        print("Campaign Member found, updating status to Checked In")
        campaignMemberID = campaignMemberQuery['records'][0]['Id']
        result = sf.CampaignMember.update(campaignMemberID, {'Attendee_Status__c': 'Checked In'})
        print("Done.")
    else:
        print("Campaign member not found, skipping...")


# Responds to eventbrite's request so eventbrite will not resend information
def respond(request):
    print("request recieved")
    requestJSON = request.get_json()  # Convert request object to dictionary
    print(requestJSON)
    if requestJSON:
        action = requestJSON['config']['action']
        if (action == "event.published"):
            createEvent(requestJSON['api_url'])
            return Response(status=200)
        if (action == "order.placed"):
            processOrder(requestJSON['api_url'])
            return Response(status=200)
        if (action == "attendee.checked_in" or action == "barcode.checked_in"):
            processCheckin(requestJSON['api_url'])
            return Response(status=200)
        if (action == "test"):
            sf = getSalesforce()
            r = requests.get("https://www.eventbriteapi.com/v3/users/me", headers=AUTH_HEADER_EB)
            if r.status_code == 200:
                eventID = createEvent(TEST_EVENT_URL)
                sf.Campaign.delete(eventID)
                return Response("Recieved request from eventbrite. Successfully authenticated to Eventbrite and Salesforce.")
            else:
                return Response("Check credentials file. Invalid credentials detected.")
    return Response("Ready to process data.")
