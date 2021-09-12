import json
import requests
import time
import pathlib

#Returns a list of each parking providers' organization number
def fetchParkingProviders():
    retList = []
    #Queries Statens Vegvesen for a list of parking providers
    r = requests.get("https://www.vegvesen.no/ws/no/vegvesen/veg/parkeringsomraade/parkeringsregisteret/v1/parkeringstilbyder/",
            headers = {'accept': 'application/json'})
    jsonData = json.loads(r.text)

    #Filter out everything except the organization number from the data. 
    for v in jsonData:
        retList.append(v["organisasjonsnummer"])

    return retList


def createFullJsonFile():
    print("It can take some time before it starts..")
    #Get a list of every parking provider
    parkingProvidersList = fetchParkingProviders()

    #Create the file path for the json file that will be created.
    parkingInformationFilePath = str(pathlib.Path(__file__).parent.resolve()) + "/../data/parkingInformation.json"
    f = open(parkingInformationFilePath, "wb")
    #The start of the JSON file. Each parking provider will become an element in the list.
    f.write(b"[")

    #Loops through the list of parking providers, and adds each parking facility to the json file.
    for index, v in enumerate(parkingProvidersList, start = 1):
        progressText = str(index) + "/" + str(len(parkingProvidersList))
        #Use the parking provder's organization number to query data for the specific parking provider
        try:
            parkingProviderUrl = "https://www.vegvesen.no/ws/no/vegvesen/veg/parkeringsomraade/parkeringsregisteret/v1/parkeringstilbyder/" + str(v)
            r = requests.get(parkingProviderUrl, headers = {'accept': 'application/json'}, timeout=10)

            if (r.status_code == 200):
                if (index != 1):
                    #To seperate each item in the list.
                    f.write(b",")
                f.write(r.content)
                print(progressText)
            elif (r.status_code == 429):
                #This error code means that the API wants us to wait.
                sleepTime = int(r.headers["Retry-After"])
                print(progressText + ": We will have to wait " + str(sleepTime) + "s")
                #Wait for the time 
                time.sleep(sleepTime)
            else:
                print(progressText + ": [ERROR] No handling routines for the code: " + str(r.status_code))

        except requests.exceptions.ReadTimeout:
            print(progressText + ": [WARNING] Read timeout")

    #End the list.
    f.write(b"]")
    f.close()
    print("Done!")


if __name__ == "__main__":
    createFullJsonFile()
