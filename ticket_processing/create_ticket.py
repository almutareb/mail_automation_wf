import requests
import os
import dotenv
import json

dotenv.load_dotenv()

auth_token = os.getenv('HUBSPOT_AUTH_TOKEN')

contacts_endpoint = "https://api.hubapi.com/crm/v3/objects/contacts?limit=10&archived=false"
tickets_endpoint = "https://api.hubapi.com/crm/v3/objects/tickets"

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

# headers = {
#     'authorization': 'Bearer '+auth_token,
#     'Content-Type': 'application/json'}
# data = {''} 

#r = requests.get(contacts_endpoint, auth=BearerAuth(auth_token))
def create_hs_ticket(params):
    ticket_payload = {
        "properties": {
            "hs_pipeline_stage": "1",
            "subject": params['subject'],
            "assigned_unit": params['category'],
            "content": params['body']
        }

    }

    r = requests.post(tickets_endpoint, auth=BearerAuth(auth_token), json=ticket_payload)



    return r.json()

with open(file='working/emails_json/1903f6c3d3b29017.json', mode='r') as file:
    emails_json = json.load(file)
create_hs_ticket(emails_json)