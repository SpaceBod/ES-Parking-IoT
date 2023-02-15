import  hashlib
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


salt = "5gz"
def getallspaces():
    path = "parkingspaces.json"
    resp = authed_session.get(db+path)
    all = resp.json()
    new = []
    for index, space in enumerate(all):
        if space is not None:
            if space['Free'] == "True":
                f = "Yes"
            else:
                f = "No"
            new.append({"space": index, "free": f, "type": space['Type']})
    return new

def parkinggen():
    path = "parkingspaces.json"
    resp = authed_session.get(db+path)
    all = resp.json()
    new = []
    for index, space in enumerate(all):
        if space is not None:
            if space['Free'] == "True":
                f = True
            else:
                f = False
            new.append([index, f, space['Type']])
    return new

def adduser(username,password,card):
    path = f"users/{username}.json"

    database_password = password + salt
    hashedpass = hashlib.md5(database_password.encode())
    data = {"hashpass":hashedpass.hexdigest(), "card":str(card)}
    print(data["hashpass"])

    print("Writing {} to {}".format(data, path))
    resp = authed_session.push(db + path, json=data)


def userlogin(username,password):
    path = f"users/{username}.json"
    resp = authed_session.get(db+path)
    details = resp.json()
    if details is not None:
        hashpass = details['hashpass']
    else:
        hashpass = 0
    passsalt = password+salt
    givenpasshash = hashlib.md5(passsalt.encode()).hexdigest()
    if(hashpass != givenpasshash):
        print("login failed")
        return False, None, None
    else:
        card = details['card']
        rfidpath = f"rfidcards/{card}.json"
        rfresp = authed_session.get(db+rfidpath)
        if 'plate' in list(details.keys()):
            plate = details['plate']
        else:
            plate = "None added"
        return True, rfresp.json(), plate

def updatepref(card, pref):
    path = f"rfidcards/{card}.json"
    update = {"Preference": pref}
    resp = authed_session.patch(db + path, json=update)
    if resp.ok:
        print("updated pref")
    else:
        print(resp.json())
        raise

def updatetype(card, type):
    path = f"rfidcards/{card}.json"
    update = {"Type": type}
    resp = authed_session.patch(db + path, json=update)
    if resp.ok:
        print("updated type")
    else:
        print(resp.json())
        raise

def addplate(plate, name):
    platepath = "numberplates.json"
    platedata = {plate:name}
    plateresp = authed_session.patch(db+platepath, json=platedata)
    if plateresp.ok:
        print("added plate to plates part:", platedata)
    else:
        print(plateresp.json())

    userspath = f"users/{name}.json"
    usersdata = {"plate":plate}
    usersresp = authed_session.patch(db+userspath, json=usersdata)
    if usersresp.ok:
        print("added plate to users part:", usersdata)
    else:
        print(usersresp.json())

def adduser(username,password,card):
    path = f"users/{username}.json"

    database_password = password + salt
    hashedpass = hashlib.md5(database_password.encode())
    data = {"hashpass":hashedpass.hexdigest(), "card":str(card)}
    print(data["hashpass"])

    print("Writing {} to {}".format(data, path))
    resp = authed_session.put(db + path, json=data)

    if resp.ok:
        print("done")
    else:
        print(resp.json())
    return 0

def getrfid(username):
    path = f"users/{username}.json"
    resp = authed_session.get(db+path)

    card = resp.json()["card"]
    return card

def getstats():
    path = "stats.json"
    resp = authed_session.get(db+path)
    return resp.json()