import requests
import os
import dotenv

dotenv.load_dotenv()

auth_token = os.getenv('HUBSPOT_AUTH_TOKEN')

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

contacts_endpoint = "https://api.hubapi.com/crm/v3/objects/contacts?limit=10&archived=false"
tickets_endpoint = "https://api.hubapi.com/crm/v3/objects/tickets"

# headers = {
#     'authorization': 'Bearer '+auth_token,
#     'Content-Type': 'application/json'}
# data = {''} 

r = requests.get(contacts_endpoint, auth=BearerAuth(auth_token))

ticket_payload = {

}

#requests.post(tickets_endpoint, json=ticket_payload)




print(r.json())