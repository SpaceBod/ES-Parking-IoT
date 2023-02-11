import re

def addnumberplate(filename, numberplate):
    
    filename = filename[:-4] #take out .jpg
    split = filename.split('_')
    rfid = split[0]
    date = split[1]
    time = split[2]
    time = re.sub("/",":",time)
    path = "rfidcards/{}/{}/In/.json".format(rfid,date)
    resp = requests.get(db+path)
    resp = resp.json()

    for num, item in enumerate(resp):

        if item == time:
            resp[num] = item+"_"+numberplate

    update = {}
    for i, obj in enumerate(resp):
        update[i] = obj

    newresp = requests.patch(db+path, json=update)

    if newresp.ok:
        print("added number plate to database")
    else:
        print(newresp.json())
        raise
        


#Need the filename to be in this format: rfidnumber_date_time.jpg
#just call function with that filename and numberplate as input
