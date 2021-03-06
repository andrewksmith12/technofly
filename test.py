from os import truncate
import main
from simple_salesforce import format_soql
import json
import requests
# done = []
# eventList = ["136466040601", "137489437609", "136012612385", "149906679915", "144704734757", "151257855317", "148367736895", "148684261629", "136009757847", "149178313351", "149960466793", "141374778769", "150621160947", "132578855927", "136015085783", "136014315479", "139708432683", "150825066835", "145939824945", "136016090789", "150629279229", "144673525409", "132583058497", "150631180917", "150630717531", "132578908083", "144704748799", "150638575033", "149915205415", "150625670435", "149914212445", "144674456193", "144704768859", "150625850975", "149902457285", "150601628525", "144674887483", "144704778889", "144704800955"]
# eventcount = len(eventList)
# ordercount = 0
# removed = []
# print(len(eventList))
# for eventID in eventList:
#     print("Processing Event ID: "+eventID)
#     api_url_create = "https://www.eventbriteapi.com/v3/events/"+eventID
#     main.createEvent(api_url_create)
#     api_url = "https://www.eventbriteapi.com/v3/events/"+eventID+"/orders"
#     print(api_url)
#     r = requests.get(api_url, headers=main.AUTH_HEADER_EB, params={"expand":["category","promotional_code"]})
#     r = r.json()
#     for order in r['orders']:
#         ordercount+=1
#         print("Processing order: "+order['id']+" in event: "+eventID)
#         main.processOrder(order['resource_uri'])
# print("Event Count: "+str(eventcount))
# print("Order Count: "+str(ordercount))

# r = requests.get("https://www.eventbriteapi.com/v3/orders/1662981183", headers=main.AUTH_HEADER_EB, params={"expand":["category","promotional_code"]})
# r = r.json()
# main.processOrder(r['resource_uri'])

# attendees = {'pagination': {'object_count': 4, 'page_number': 1, 'page_size': 50, 'page_count': 1, 'has_more_items': False}, 'attendees': [{'costs': {'base_price': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'eventbrite_fee': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'gross': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'payment_fee': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'tax': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}}, 'resource_uri': 'https://www.eventbriteapi.com/v3/orders/1594288627/attendees/2225263465/', 'id': '2225263465', 'changed': '2021-01-28T16:33:26Z', 'created': '2021-01-28T16:33:26Z', 'quantity': 1, 'variant_id': None, 'profile': {'first_name': 'Sarah ', 'last_name': 'Dallas', 'addresses': {}, 'company': 'Mobile Loaves & Fishes, Inc. ', 'name': 'Sarah  Dallas', 'email': 'sarah.dallas@mlf.org', 'job_title': 'Asst. Director of Resident Care'}, 'barcodes': [{'status': 'unused', 'barcode': '15942886272225263465001', 'created': '2021-01-28T16:33:27Z', 'changed': '2021-01-28T16:33:27Z', 'checkin_type': 0, 'is_printed': False, 'qr_code_url': 'https://www.eventbriteapi.com/qrcode/15942886272225263465001/?sig=AHTu1ybCLicNGHy1tudXRdabY_D05ZRSLw'}], 'answers': [{'answer': 'Member', 'question': 'How did you hear about this event?', 'type': 'text', 'question_id': '39206233'}, {'answer': 'No', 'question': 'Do you identify as black, indigenous, and/or a person of color? ', 'type': 'multiple_choice', 'question_id': '39206235'}, {'answer': 'White or Caucasian', 'question': 'What is your race? Check all that apply.', 'type': 'multiple_choice', 'question_id': '39206237'}], 'checked_in': False, 'cancelled': False, 'refunded': False, 'affiliate': 'oddtdteb', 'guestlist_id': None, 'invited_by': None, 'status': 'Attending', 'ticket_class_name': 'Member Ticket', 'delivery_method': 'electronic', 'event_id': '136009757847', 'order_id': '1594288627', 'ticket_class_id': '237170043', 'promotional_code': {'resource_uri': 'https://www.eventbriteapi.com/v3/events/136009757847/discounts/511380376/', 'id': '511380376', 'promotion': '100.00% - UNLIMITED2020', 'promotion_type': 'discount', 'code': 'UNLIMITED2020', 'percent_off': '100.00'}}, {'costs': {'base_price': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'eventbrite_fee': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'gross': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'payment_fee': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'tax': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}}, 'resource_uri': 'https://www.eventbriteapi.com/v3/orders/1594288627/attendees/2225263467/', 'id': '2225263467', 'changed': '2021-01-28T16:33:26Z', 'created': '2021-01-28T16:33:26Z', 'quantity': 1, 'variant_id': None, 'profile': {'first_name': 'Carlos', 'last_name': 'Guerra', 'addresses': {}, 'company': 'Mobile Loaves & Fishes, Inc. ', 'name': 'Carlos Guerra', 'email': 'carlos.guerra@mlf.org', 'job_title': 'Neighbor Engagement Manager'}, 'barcodes': [{'status': 'unused', 'barcode': '15942886272225263467001', 'created': '2021-01-28T16:33:27Z', 'changed': '2021-01-28T16:33:27Z', 'checkin_type': 0, 'is_printed': False, 'qr_code_url': 'https://www.eventbriteapi.com/qrcode/15942886272225263467001/?sig=AHTu1yZD-KydApISQZEEM0jwF-CRQ3kzLQ'}], 'answers': [{'answer': 'Member', 'question': 'How did you hear about this event?', 'type': 'text', 'question_id': '39206233'}, {'answer': 'Yes', 'question': 'Do you identify as black, indigenous, and/or a person of color? ', 'type': 'multiple_choice', 'question_id': '39206235'}, {'answer': 'LatinX or Hispanic', 'question': 'What is your race? Check all that apply.', 'type': 'multiple_choice', 'question_id': '39206237'}], 'checked_in': False, 'cancelled': False, 'refunded': False, 'affiliate': 'oddtdteb', 'guestlist_id': None, 'invited_by': None, 'status': 'Attending', 'ticket_class_name': 'Member Ticket', 'delivery_method': 'electronic', 'event_id': '136009757847', 'order_id': '1594288627', 'ticket_class_id': '237170043', 'promotional_code': {'resource_uri': 'https://www.eventbriteapi.com/v3/events/136009757847/discounts/511380376/', 'id': '511380376', 'promotion': '100.00% - UNLIMITED2020', 'promotion_type': 'discount', 'code': 'UNLIMITED2020', 'percent_off': '100.00'}}, {'costs': {'base_price': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'eventbrite_fee': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'gross': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'payment_fee': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'tax': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}}, 'resource_uri': 'https://www.eventbriteapi.com/v3/orders/1594288627/attendees/2225263469/', 'id': '2225263469', 'changed': '2021-01-28T16:33:26Z', 'created': '2021-01-28T16:33:26Z', 'quantity': 1, 'variant_id': None, 'profile': {'first_name': 'Justin', 'last_name': 'Case', 'addresses': {}, 'company': 'Mobile Loaves & Fishes, Inc. ', 'name': 'Justin Case', 'email': 'karen@mlf.org', 'job_title': 'Resident Care Data Specialist'}, 'barcodes': [{'status': 'unused', 'barcode': '15942886272225263469001', 'created': '2021-01-28T16:33:27Z', 'changed': '2021-01-28T16:33:27Z', 'checkin_type': 0, 'is_printed': False, 'qr_code_url': 'https://www.eventbriteapi.com/qrcode/15942886272225263469001/?sig=AHTu1yYteDcwRUIdqty8w9sNMrgm4V90FQ'}], 'answers': [{'answer': 'Member', 'question': 'How did you hear about this event?', 'type': 'text', 'question_id': '39206233'}, {'answer': 'Prefer not to say', 'question': 'Do you identify as black, indigenous, and/or a person of color? ', 'type': 'multiple_choice', 'question_id': '39206235'}, {'answer': 'Prefer not to say', 'question': 'What is your race? Check all that apply.', 'type': 'multiple_choice', 'question_id': '39206237'}], 'checked_in': False, 'cancelled': False, 'refunded': False, 'affiliate': 'oddtdteb', 'guestlist_id': None, 'invited_by': None, 'status': 'Attending', 'ticket_class_name': 'Member Ticket', 'delivery_method': 'electronic', 'event_id': '136009757847', 'order_id': '1594288627', 'ticket_class_id': '237170043', 'promotional_code': {'resource_uri': 'https://www.eventbriteapi.com/v3/events/136009757847/discounts/511380376/', 'id': '511380376', 'promotion': '100.00% - UNLIMITED2020', 'promotion_type': 'discount', 'code': 'UNLIMITED2020', 'percent_off': '100.00'}}, {'costs': {'base_price': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'eventbrite_fee': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'gross': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'payment_fee': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}, 'tax': {'display': '$0.00', 'currency': 'USD', 'value': 0, 'major_value': '0.00'}}, 'resource_uri': 'https://www.eventbriteapi.com/v3/orders/1594288627/attendees/2225263471/', 'id': '2225263471', 'changed': '2021-01-28T16:33:26Z', 'created': '2021-01-28T16:33:26Z', 'quantity': 1, 'variant_id': None, 'profile': {'first_name': 'Ima', 'last_name': 'Special', 'addresses': {}, 'company': 'Mobile Loaves & Fishes, Inc. ', 'name': 'Ima Special', 'email': 'karen@mlf.org', 'job_title': 'PM Neighbor Adminisrator'}, 'barcodes': [{'status': 'unused', 'barcode': '15942886272225263471001', 'created': '2021-01-28T16:33:27Z', 'changed': '2021-01-28T16:33:27Z', 'checkin_type': 0, 'is_printed': False, 'qr_code_url': 'https://www.eventbriteapi.com/qrcode/15942886272225263471001/?sig=AHTu1ybpHzK2gWO2BcJ5B27Hc_tWD_41zA'}], 'answers': [{'answer': 'Prefer not to say', 'question': 'Do you identify as black, indigenous, and/or a person of color? ', 'type': 'multiple_choice', 'question_id': '39206235'}, {'answer': 'Prefer not to say', 'question': 'What is your race? Check all that apply.', 'type': 'multiple_choice', 'question_id': '39206237'}], 'checked_in': False, 'cancelled': False, 'refunded': False, 'affiliate': 'oddtdteb', 'guestlist_id': None, 'invited_by': None, 'status': 'Attending', 'ticket_class_name': 'Member Ticket', 'delivery_method': 'electronic', 'event_id': '136009757847', 'order_id': '1594288627', 'ticket_class_id': '237170043', 'promotional_code': {'resource_uri': 'https://www.eventbriteapi.com/v3/events/136009757847/discounts/511380376/', 'id': '511380376', 'promotion': '100.00% - UNLIMITED2020', 'promotion_type': 'discount', 'code': 'UNLIMITED2020', 'percent_off': '100.00'}}]}

# attendee = attendees['attendees'][0]
# r = requests.get("https://www.eventbriteapi.com/v3/orders/1680480479/attendees", headers=main.AUTH_HEADER_EB, params={"expand":["category","promotional_code"]})
# attendees = r.json()


# sf = main.getSalesforce()


# for attendee in attendees['attendees']:
#     #print("SELECT Id, Name from Account WHERE Name LIKE '{ebOrg}'".format(ebOrg=attendee['profile']['company']).strip().replace('"', '\"').replace("'", "\'").replace("'", "\'"))

#     accountQueryResult = sf.query(format_soql(("SELECT Id, Name from Account WHERE Name LIKE 'St. David\\'s Foundation'".format(ebOrg=attendee['profile']['company']).strip().replace('"', '\\"').replace("'", "\\'").replace("'", "\\'"))))
#     print(accountQueryResult)

# r = requests.get("https://www.eventbriteapi.com/v3/users/me", headers=main.AUTH_HEADER_EB)
# print(r.status_code == 200)


# result = sf.CampaignMember.update('00v7h000004zMVVAA2', {'status':'Attending'}) #sf.CampaignMemberStatus.create('7017h000000xP3rAAE', {'Label':'Checked In', 'HasResponded':True})


# print(result)

# sf.Campaign.delete('7017h000000xP5JAAU')

r = requests({'config': {'action': 'gcloud-test'}})
print(r.get_json)
response = main.respond(r)
print(response)
