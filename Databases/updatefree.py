from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
db = "https://embedded-systems-cf93d-default-rtdb.europe-west1.firebasedatabase.app/"
keyfile = "embedded-systems-cf93d-firebase-adminsdk-amky8-e0a50b80ba.json"
scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/firebase.database"
]

credentials = service_account.Credentials.from_service_account_file(keyfile, scopes=scopes)

authed_session = AuthorizedSession(credentials)

def updatefree(space, status):
    path = f"parkingspaces/{space}.json"

    if status == 'true':
        update = {"Free": "True"}
    else:
        update = {"Free": "False"}
        
    resp = authed_session.patch(db + path, json=update)

    if resp.ok:
        print("Updated free status of space {}".format(space))
    else:
        raise
