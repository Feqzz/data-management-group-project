import json
from owlready2 import *

onto = get_ontology("http://tisk.ml/data/parking")
parkSchema = get_ontology("http://schema.mobivoc.org/").load()


with onto:
    class ParkingCompany(parkSchema.ParkingFacility):
        pass
    class ParkingFacility(Thing):
        pass
    class ParkingLot(ParkingFacility):
        pass
    class StreetParking(ParkingFacility):
        pass
    class ParkingGarage(ParkingFacility):
        pass
    class is_operated_by(ParkingFacility):
        domain = [ParkingFacility]
        range = [ParkingCompany]
    class active(DataProperty):
        domain = [ParkingFacility]
        range = [bool]
    class deactivation_date(DataProperty):
        domain = [ParkingFacility]
        range = [datetime.datetime]
    class activation_date(DataProperty):
        domain = [ParkingFacility]
        range = [datetime.datetime]
    class handicap_information(DataProperty):
        domain = [ParkingFacility]
        range = [owlready2.locstr]
    class no_of_handicap_parking_spaces(DataProperty):
        domain = [ParkingFacility]
        range = [int]
    class no_of_electric_vehicle_chargers(DataProperty):
        domain = [ParkingFacility]
        range = [int]
    class no_of_parking_spaces_with_fee(DataProperty):
        domain = [ParkingFacility]
        range = [int]
    class no_of_parking_spaces_without_fee(DataProperty):
        domain = [ParkingFacility]
        range = [int]


def createParkingCompany(parkingCompanyInformation):
    urlString = "C" + str(parkingCompanyInformation["id"])
    #Magically adds it to the ontology
    obj = ParkingCompany(urlString, onto)
    obj.label = parkingCompanyInformation["navn"]


def createParkingFacility(parkingFacilityInformation):
    urlString = "F" + str(parkingFacilityInformation["id"])
    parkingType = parkingFacilityInformation["aktivVersjon"]["typeParkeringsomrade"]
    if (parkingType == "LANGS_KJOREBANE"):
        obj = StreetParking(urlString, onto) 
    elif (parkingType == "AVGRENSET_OMRADE"):
        obj = ParkingLot(urlString, onto)
    elif (parkingType == "PARKERINGSHUS"):
        obj = ParkingGarage(urlString, onto)
    obj.label = parkingFacilityInformation["aktivVersjon"]["navn"]


def main():
    f = open("parkingInformation.json")
    parkingInformation = json.load(f)
    for v in parkingInformation:
        createParkingCompany(v)
        for i in v["parkeringsomrader"]:
            createParkingFacility(i)
    onto.save(file = "stianParking.owl", format = "rdfxml")
    print("Done!")


if __name__ == "__main__":
    main()
