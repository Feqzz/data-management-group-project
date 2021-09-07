from rdflib import Graph, Literal, RDF, URIRef, Namespace, BNode
# rdflib knows about quite a few popular namespaces, like W3C ontologies, schema.org etc.
from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
                           PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
                           VOID, XMLNS, XSD

import requests
import json
import pandas as pd
import io
import chardet
import os
import stat

postalDf = pd.DataFrame()
municipalityUriDf = pd.DataFrame()
namespaceUrl = "http://tisk.ml/data/parking#"
g = Graph()

pns = Namespace(namespaceUrl)
# g.namespace_manager.bind("norPark", pns)
wikiprop = Namespace("https://www.wikidata.org/wiki/Property:")
g.namespace_manager.bind("wikiprop", wikiprop)
# schemaorg = Namespace("http://schema.org/")
g.namespace_manager.bind("SDO", SDO)
geo = Namespace("http://www.opengis.net/ont/geosparql#")
g.namespace_manager.bind("geo", geo)

def fillMunicipalityUriDf():
    global municipalityUriDf
    #from Wikidata
    # url = 'https://query.wikidata.org/sparql'
    # query = '''
    # PREFIX wd: <http://www.wikidata.org/entity/>
    # PREFIX wds: <http://www.wikidata.org/entity/statement/>
    # PREFIX wdv: <http://www.wikidata.org/value/>
    # PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    # PREFIX wikibase: <http://wikiba.se/ontology#>
    # PREFIX p: <http://www.wikidata.org/prop/>
    # PREFIX ps: <http://www.wikidata.org/prop/statement/>
    # PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    # PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    # PREFIX bd: <http://www.bigdata.com/rdf#>
    # SELECT DISTINCT ?municipalityCode ?municipality ?county ?country  WHERE {
    #         ?municipality p:P2504 ?statement0.
    #         ?statement0 (ps:P2504) ?municipalityCode.
    #         ?municipality p:P131 ?statement1.
    #         ?statement1 (ps:P131) ?county.
    #         ?municipality p:P17 ?statement2.
    #         ?statement2 (ps:P17) ?country.
    #         MINUS {
    #         ?municipality p:P31 ?statement3.
    #         ?statement3 (ps:P31/(wdt:P279*)) wd:Q18663579.
    #       }
    #       }

    # # '''
    # r = requests.get(url, params = {'format': 'json', 'query': query})
    # data = r.json()
    # with open("query.json", 'w') as json_file:
    #     json.dump(data, json_file)

    # from file
    with open("query.json") as json_file:
        data = json.load(json_file)

    municipalityUriDf = pd.json_normalize(data["results"]["bindings"])

def fillPostalDf():
    global postalDf
    # url = "https://www.bring.no/radgivning/sende-noe/adressetjenester/postnummer/_/attachment/download/7f0186f6-cf90-4657-8b5b-70707abeb789:676b821de9cff02aaa7a009daf0af8a2a346a1bc/Postnummerregister-ansi.txt"
    url = "post.txt"

    header_list = ["postcode", "postplace", "citycode", "city", "category"]
    postalDf = pd.read_csv(url, encoding='ISO-8859-1', sep='\t', names=header_list, dtype=str)

def getMunicipalityCodeFromPostal(postalCode):
    return postalDf.loc[postalDf['postcode'] == postalCode].iloc[0]['citycode']

def getLocationUrisFromMunicipalityCode(code):
    return municipalityUriDf.loc[municipalityUriDf['municipalityCode.value'] == code].iloc[0]

def getGeoUri(lat, long):
    geouri = f"https://geohack.toolforge.org/geohack.php?params={lat}_N_{long}_E_globe:earth&language=en"
    return geouri

# url = "https://www.vegvesen.no/ws/no/vegvesen/veg/parkeringsomraade/parkeringsregisteret/v1/parkeringsomraade"

def getParkingDict():
    f = open("parkingInformation.json")
    data = json.load(f)
    return data

def addProviderTriples(provider):
    providerUri = URIRef(pns + "C" + provider["organisasjonsnummer"])
    municipalityCode = getMunicipalityCodeFromPostal(provider["postnummer"])
    # municipalityIri = URIRef("Q13453153421")
    locationInfo = getLocationUrisFromMunicipalityCode(municipalityCode)
    municipalityIri = URIRef(locationInfo["municipality.value"])
    countyIri = URIRef(locationInfo["county.value"])
    countryIri = URIRef(locationInfo["country.value"])
    org_number_propIri = URIRef("https://www.wikidata.org/wiki/Property:P2333")

    g.add( ( providerUri, org_number_propIri, Literal( provider["organisasjonsnummer"] ) ) )
    g.add( ( providerUri, RDFS.label, Literal( provider["navn"] ) ) )
    g.add( ( providerUri, SDO.url, Literal( provider["nettsted"] ) ) )
    g.add( ( providerUri, pns.active, Literal( True if provider["status"] == "AKTIV" else False) ) )

    contactPoint = BNode()
    g.add( ( providerUri, SDO.ContactPoint, contactPoint) )
    g.add( ( contactPoint, RDF.type, SDO.ContactPoint) )
    g.add( ( contactPoint, SDO.email, Literal( provider["epost"] ) ) )
    g.add( ( contactPoint, SDO.telephone, Literal( provider["telefonnummer"] ) ) )

    address = BNode()
    g.add( ( providerUri, SDO.PostalAddress, address ) )
    g.add( ( address, RDF.type, SDO.PostalAddress ) )
    g.add( ( address, SDO.postalCode, Literal( provider["postnummer"] ) ) )
    g.add( ( address, SDO.addressLocality, municipalityIri) )
    g.add( ( address, SDO.addressRegion, countyIri) )
    g.add( ( address, SDO.addressCountry, countryIri) )

def addFacilityTriples(facility):
    facilityUri = URIRef(pns + "F" + str(facility["id"]))
    municipalityCode = getMunicipalityCodeFromPostal(facility["aktivVersjon"]["postnummer"])
    providerUri = URIRef(pns + "C" + facility["parkeringstilbyderOrganisasjonsnummer"])
    locationInfo = getLocationUrisFromMunicipalityCode(municipalityCode)
    municipalityIri = URIRef(locationInfo["municipality.value"])
    countyIri = URIRef(locationInfo["county.value"])
    countryIri = URIRef(locationInfo["country.value"])

    #g.add( ( facilityUri, RDF.type, pns.CParkingLot) )
    g.add( ( facilityUri, pns.is_operated_by, providerUri) )
    g.add( ( facilityUri, RDFS.label, Literal( facility["aktivVersjon"]["navn"] ) ) )
    address = BNode()
    g.add( ( facilityUri, SDO.PostalAddress, address ) )
    g.add( ( address, RDF.type, SDO.PostalAddress ) )
    g.add( ( address, SDO.streetAddress, Literal( facility["aktivVersjon"]["adresse"] ) ) )
    g.add( ( address, SDO.postalCode, Literal( facility["aktivVersjon"]["postnummer"] ) ) )
    g.add( ( address, SDO.addressLocality, municipalityIri) )
    g.add( ( address, SDO.addressRegion, countyIri) )
    g.add( ( address, SDO.addressCountry, countryIri) )

    g.add( ( facilityUri, pns.no_of_parking_spaces_with_fee, Literal( facility["aktivVersjon"]["antallAvgiftsbelagtePlasser"] ) ) )
    g.add( ( facilityUri, pns.no_of_parking_spaces_without_fee, Literal( facility["aktivVersjon"]["antallAvgiftsfriePlasser"] ) ) )
    g.add( ( facilityUri, pns.no_of_electric_vehicle_chargers, Literal( facility["aktivVersjon"]["antallLadeplasser"] ) ) )
    g.add( ( facilityUri, pns.no_of_handicap_parking_spaces, Literal( facility["aktivVersjon"]["antallForflytningshemmede"] ) ) )
    g.add( ( facilityUri, pns.no_of_handicap_parking_spaces, Literal( facility["aktivVersjon"]["antallForflytningshemmede"], datatype=XSD.unsignedInt ) ) )
    g.add( ( facilityUri, pns.handicap_information, Literal( facility["aktivVersjon"]["vurderingForflytningshemmede"], lang="no") ) )
    g.add( ( facilityUri, wikiprop.P625, Literal( f"Point({facility['breddegrad']} {facility['lengdegrad']})", datatype=geo.wktLiteral ) ) )

    g.add( ( facilityUri, pns.activation_date, Literal( facility["aktivVersjon"]["aktiveringstidspunkt"], datatype=XSD.dateTime ) ) )
    if(facility["deaktivert"] != None):
        g.add( ( facilityUri, pns.deactivation_date, Literal( facility["aktivVersjon"]["aktiveringstidspunkt"], datatype=XSD.dateTime ) ) )


    parkingType = facility["aktivVersjon"]["typeParkeringsomrade"]
    if (parkingType == "LANGS_KJOREBANE"):
        g.add( (facilityUri, RDF.type, pns.StreetParking) )
    elif (parkingType == "AVGRENSET_OMRADE"):
        g.add( (facilityUri, RDF.type, pns.ParkingLot) )
    elif (parkingType == "PARKERINGSHUS"):
        g.add( (facilityUri, RDF.type, pns.ParkingGarage) )


def addOntology():
    uri = URIRef(pns + "is_operated_by")
    g.add( (uri, RDF.type, RDF.Property ) )
    g.add( (uri, RDFS.label, Literal("Placeholder") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    #g.add( (uri, RDFS.domain, URIRef(pns + "ParkingLot") ) )
    #g.add( (uri, RDFS.domain, URIRef(pns + "ParkingGarage") ) )
    #g.add( (uri, RDFS.domain, URIRef(pns + "StreetParking") ) )
    g.add( (uri, RDFS.range, URIRef(pns + "ParkingCompany") ) )


    uri = URIRef(pns + "active")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("Tells if the parking facility is active or not.") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.boolean) )


    uri = URIRef(pns + "deactivation_date")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("The date the Parking facility was deactivated.") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.dateTime) )


    uri = URIRef(pns + "activation_date")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("The date the Parking facility was activated.") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.dateTime) )


    uri = URIRef(pns + "handicap_information")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("Handicap information for the parking facility.") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.string) )


    uri = URIRef(pns + "no_of_parking_spaces_without_fee")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("Number of parking spaces without a fee.") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.integer) )


    uri = URIRef(pns + "no_of_parking_spaces_with_fee")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("Number of parking spaces with a fee.") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.integer) )


    uri = URIRef(pns + "no_of_handicap_parking_spaces")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("Number of handicap parking spaces.") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.integer) )


    uri = URIRef(pns + "no_of_electric_vehicle_chargers")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("Number of electric vehicle chargers.") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.integer) )


    uri = URIRef(pns + "ParkingCompany")
    g.add( (uri, RDF.type, RDFS.Class) )
    g.add( (uri, RDFS.subClassOf, URIRef("http://schema.mobivoc.org/#ParkingFacility") ) )


    uri = URIRef(pns + "ParkingFacility")
    g.add( (uri, RDF.type, RDFS.Class) )
    g.add( (uri, RDFS.subClassOf, URIRef(pns + "ParkingCompany") ) )


    uri = URIRef(pns + "ParkingLot")
    g.add( (uri, RDF.type, RDFS.Class) )
    g.add( (uri, RDFS.subClassOf, URIRef(pns + "ParkingFacility") ) )


    uri = URIRef(pns + "ParkingGarage")
    g.add( (uri, RDF.type, RDFS.Class) )
    g.add( (uri, RDFS.subClassOf, URIRef(pns + "ParkingFacility") ) )


    uri = URIRef(pns + "StreetParking")
    g.add( (uri, RDF.type, RDFS.Class) )
    g.add( (uri, RDFS.subClassOf, URIRef(pns + "ParkingFacility") ) )


def fillGraph(parkDict):
    for v in parkDict:
        addProviderTriples(v)
        for i in v["parkeringsomrader"]:
            addFacilityTriples(i)

    #http://wifo5-03.informatik.uni-mannheim.de/bizer/pub/LinkedDataTutorial/#whichvocabs
    # g.serialize(destination="../tisk.ml/public/data/parking.rdf", format="xml")
    # g.serialize(destination="parking.rdf", format="xml")
    #g.serialize(destination="parking.ttl")

def main():
    fillPostalDf()
    fillMunicipalityUriDf()
    parkDict = getParkingDict()

    print("Adding ontology..")
    addOntology()
    print("Adding entities..")
    fillGraph(parkDict)

    #Save the file
    # g.serialize(destination="parking.ttl")
    # os.chmod("parking.ttl", stat.S_IROTH)

    g.serialize(destination="parking.rdf", format="xml")
    # os.chmod("parking.rdf", stat.S_IROTH)

    print("Done!")


if __name__ == '__main__':
    main()
