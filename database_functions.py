import requests, time, random, json, datetime

#to update an item, just rewrite to object using .put and path with .format(1001)
db = "https://embedded-systems-cf93d-default-rtdb.europe-west1.firebasedatabase.app/"



def rfiduserinout(card, inout):
    date = datetime.date.today()
    path = f"rfidcards/{card}/{date}.json"

    read = requests.get(db+path)
    data = read.json()
    if inout == "in":

        data["In"]= datetime.datetime.now().strftime("%H:%M:%S")

    else:
        data["Out"]= datetime.datetime.now().strftime("%H:%M:%S")

    resp = requests.put(db+path, json=data)

    if resp.ok:
        print("Ok")


def addspaces():
    noofspaces = 100
    n = 0
    while n < noofspaces+1:
        path = "parkingspaces/{}.json".format(n)  # format(1001) makes object 1001
        data = {"Free": False, "Paid": False}  # within 1001

        print("Writing {} to {}".format(data, path))
        response = requests.put(db + path, json=data)

        if response.ok:
            print("Ok")
        else:
            raise ConnectionError("Could not write to database: {}".format(response.text))
        time.sleep(0.1)
        n += 1

def readspace(space): #read specific space
    path = f"parkingspaces/{space}.json"
    resp = requests.get(db+path)
    obj = resp.json() #do obj["Free"] or obj["Paid"] for individual bits
    print(obj)

def getall():
    path = "parkingspaces/{}.json"
    resp = requests.get(db+path)
    print(resp.json())

if __name__ == '__main__':

    #addspaces()
    #readspace(20)
    rfiduserinout(1,"in")

#alters space 20
   # path = "parkingspaces/{}.json".format(20)  # format(20) alters obj 20
    #data = {"Free": True, "Paid": False}  # within 20
   # response = requests.put(db + path, json=data)
