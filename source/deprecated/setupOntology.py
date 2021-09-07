
from owlready2 import *
set_log_level(9)




onto = get_ontology("http://tisk.ml/ontology/parking")
parkSchema = get_ontology("http://schema.mobivoc.org/").load()
db = get_ontology("file:///home/kent/Downloads/ontology--DEV_type=parsed.owl").load()
onto.imported_ontologies.append(parkSchema)
onto.imported_ontologies.append(db)



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
    class City(Thing):
        pass

    class operates(ObjectProperty):
        domain = [ParkingCompany]
        range = [ParkingFacility]
    class is_in_city(ObjectProperty):
        domain = [ParkingFacility]
        range = [City]
    class no_of_parking_spaces_with_fee(DataProperty):
        domain = [ParkingFacility]
        range = [int]
    class no_of_parking_spaces_without_fee(DataProperty):
        domain = [ParkingFacility]
        range = [int]
    class no_of_electric_vehicle_chargers(DataProperty):
        domain = [ParkingFacility]
        range = [int]
    class no_of_handicap_parking_spaces(DataProperty):
        domain = [ParkingFacility]
        range = [int]
    class name(DataProperty):
        domain = [ParkingFacility, ParkingCompany]
        range = [str]
    class address(DataProperty):
        domain = [ParkingFacility, ParkingCompany]
        range = [str]
    class postalCode(DataProperty):
        domain = [ParkingFacility]
        range = [str]
    class phone_number(DataProperty):
        domain = [ParkingCompany]
        range = [str]
    class email(DataProperty):
        domain = [ParkingCompany]
        range = [str]
    class organization_number(DataProperty):
        domain = [ParkingCompany]
        range = [str]
    class latitude(DataProperty):
        domain = [ParkingFacility]
        range = [float]
    class longitude(DataProperty):
        domain = [ParkingFacility]
        range = [float]
    class deactivated(DataProperty):
        domain = [ParkingFacility]
        range = [bool]
    class activation_date(DataProperty):
        domain = [ParkingFacility]
        range = [datetime.datetime]
    class deactivation_date(DataProperty):
        domain = [ParkingFacility]
        range = [datetime.datetime]


aalesundParkering = ParkingCompany("Ålesund Parkering AS", onto, has_for_active_principle = [address])
aalesundParkering.label = "Ålesund Parkering AS"
aalesundParkering.organization_number = ["930475610"]
aalesundParkering.address = ["Nedre Strandgate 31A"]
aalesundParkering.phone_number = ["70162128"]
aalesundParkering.email = ["alesund.parkering@alesund.kommune"]

aalesund = City(Thing, onto)

skateflua = ParkingLot("skaregata 1A", onto)
skateflua.label = ["Skaregate 1a"]
skateflua.address = ["Skaregata 1A"]
skateflua.PostalCode = ["6002"]
skateflua.City = aalesund
skateflua.latitude = ["62.47"]
skateflua.longitude = ["6.15"]
skateflua.deactivated = [False]
skateflua.no_of_parking_spaces_with_fee = [15]
skateflua.no_of_parking_spaces_without_fee = [0]
skateflua.no_of_electric_vehicle_chargers = [0]
skateflua.no_of_handicap_parking_spaces = [0]
skateflua.comment = ["HC plasser i tilknytning til stedet"]
skateflua.activation_date = [datetime.datetime(2016, 12, 22, 0, 0, 0)]

# lotType = lot["aktivVersjon"]["typeParkeringsomrade"]
# if(lotType == "AVGRENSET_OMRÅDE"):
# elif(lotType == "LANGS_KJOREBANE"):
# elif(lotType == "PARKERINGSHUS"):

aalesundParkering.operates = [skateflua]



with onto:
    sync_reasoner()


onto.save(file = "parking.owl", format = "rdfxml")
