import re, requests

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


def addnumberplate(filename, numberplate):
    filename = filename[:-4]  # take out .jpg
    split = filename.split('_')
    rfid = split[0]
    date = split[1]
    time = split[2]
    time = re.sub("t", ":", time)
    path = "rfidcards/{}/{}/In/.json".format(rfid, date)
    print(rfid, date, time, path, numberplate)
    resp = requests.get(db + path)
    resp = resp.json()

    for num, item in enumerate(resp):

        if item == time:
            resp[num] = item + "_" + numberplate

    update = {}
    for i, obj in enumerate(resp):
        update[i] = obj

    newresp = authed_session.patch(db + path, json=update)

    if newresp.ok:
        print("added number plate to database")
    else:
        print(newresp.json())
        raise

def getstats():
    path = "stats.json"
    resp = authed_session.get(db+path)
    return resp.json()


if __name__ == '__main__':
    filename = ('34d6a43e_2023-02-11_18t14t40.png')
    numberplate = "WQ12PSN"
    print(numberplate)
    #addnumberplate(filename, numberplate)
    print(getstats())
