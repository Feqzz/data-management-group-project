import json
import requests
import time

def fetchParkingProviders():
    parkingProvdersList = []
    r = requests.get("https://www.vegvesen.no/ws/no/vegvesen/veg/parkeringsomraade/parkeringsregisteret/v1/parkeringstilbyder/",
            headers = {'accept': 'application/json'})
    jsonData = json.loads(r.text)

    for v in jsonData:
        parkingProvidersList.append(v["organisasjonsnummer"])

    return parkingProviderList

def createFullJsonFile():
    parkingProvidersList = fetchParkingProviders()

    f = open("parkingInformation.json", "wb")
    #The start of the JSON file. Each parking provider will become an element in the list.
    f.write(b"[")

    for index, v in enumerate(parkingProvidersList, start = 1):
        progressText = str(index) + "/" + str(len(parkingProvidersList) - 1)
        parkingProviderUrl = "https://www.vegvesen.no/ws/no/vegvesen/veg/parkeringsomraade/parkeringsregisteret/v1/parkeringstilbyder/" + str(v)
        r = requests.get(parkingProviderUrl, headers = {'accept': 'application/json'})

        if (r.status_code == 200):
            if (index != 1):
                #To seperate each item in the list.
                f.write(b",")
            f.write(r.content)
            print(progressText)
        elif (r.status_code == 429):
            sleepTime = int(r.headers["Retry-After"])
            print(progressText + ": We will have to wait " + str(sleepTime) + "s")
            time.sleep(sleepTime)
        else:
            print(progressText + ": No handling routines for the code: " + str(r.status_code))

    #End the list.
    f.write(b"]")
    f.close()

if __name__ == "__main__":
    createFullJsonFile()
