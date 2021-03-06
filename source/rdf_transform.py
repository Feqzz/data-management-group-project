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
import pathlib
import re
import sys

#Define global datastructures
postalDf = pd.DataFrame()
municipalityUriDf = pd.DataFrame()
namespaceUrl = "http://norpark.ml/"
g = Graph()

#Define and bind namespaces to graph
pns = Namespace(namespaceUrl)
g.namespace_manager.bind("norpark", pns)
wikiprop = Namespace("https://www.wikidata.org/wiki/Property:")
g.namespace_manager.bind("wikiprop", wikiprop)
g.namespace_manager.bind("schema-org", SDO)
geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
g.namespace_manager.bind("geo", geo)
geog = Namespace("http://www.opengis.net/ont/geosparql#")

#Solution to filter out illegal characters in XML, solution taken from:
#https://stackoverflow.com/questions/1707890/fast-way-to-filter-illegal-xml-unicode-chars-in-python
def genereateIllegalXmlCharactersRegex():
    #List of illegal characters
    illegal_unichrs = [(0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F),
                        (0x7F, 0x84), (0x86, 0x9F),
                        (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF)]
    if (sys.maxunicode >= 0x10000):
        illegal_unichrs.extend([(0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF),
                                (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF),
                                (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
                                (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF),
                                (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF),
                                (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
                                (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF),
                                (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF)])
    illegal_ranges = [fr'{chr(low)}-{chr(high)}' for (low, high) in illegal_unichrs]
    #Creates a regex string for the illegal characters.
    xml_illegal_character_regex = '[' + ''.join(illegal_ranges) + ']'
    return re.compile(xml_illegal_character_regex)

#defines the regex to be used later
illegalXmlCharactersRegex = genereateIllegalXmlCharactersRegex()


#Query wikidata for all municipalities in Norway, fill data structure with information
def fillMunicipalityUriDf():
    global municipalityUriDf
    #from Wikidata
    url = 'https://query.wikidata.org/sparql'
    #Define query
    query = '''
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wds: <http://www.wikidata.org/entity/statement/>
    PREFIX wdv: <http://www.wikidata.org/value/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX bd: <http://www.bigdata.com/rdf#>
    SELECT DISTINCT ?municipalityCode ?municipality ?county ?country  WHERE {
            ?municipality p:P2504 ?statement0.
            ?statement0 (ps:P2504) ?municipalityCode.
            ?municipality p:P131 ?statement1.
            ?statement1 (ps:P131) ?county.
            ?municipality p:P17 ?statement2.
            ?statement2 (ps:P17) ?country.

            MINUS {
                ?municipality p:P31 ?statement3.
                ?statement3 (ps:P31/(wdt:P279*)) wd:Q18663579.
            }
    }
    '''

    #perform query
    r = requests.get(url, params = {'format': 'json', 'query': query}, headers={'User-Agent': 'norpark.ml'})
    data = r.json()
    #Transform response to pandas dataframe
    municipalityUriDf = pd.json_normalize(data["results"]["bindings"])

#Gather postal number data from Bring, and fille dataframe
def fillPostalDf():
    global postalDf
    postalDataPath = "https://www.bring.no/radgivning/sende-noe/adressetjenester/postnummer/_/attachment/download/7f0186f6-cf90-4657-8b5b-70707abeb789:676b821de9cff02aaa7a009daf0af8a2a346a1bc/Postnummerregister-ansi.txt"

    header_list = ["postcode", "postplace", "citycode", "city", "category"]
    postalDf = pd.read_csv(postalDataPath, encoding='ISO-8859-1', sep='\t', names=header_list, dtype=str)

#Fill datastructure for parking, based on json file
def getParkingDict():
    #Uses the JSON file created with data from Statens Vegvesen
    parkingInformationFilePath = str(pathlib.Path(__file__).parent.resolve()) + "/../data/parkingInformation.json"
    f = open(parkingInformationFilePath)
    data = json.load(f)
    return data

#Helper functions:
def getMunicipalityCodeFromPostal(postalCode):
    return postalDf.loc[postalDf['postcode'] == postalCode].iloc[0]['citycode']
def getLocationUrisFromMunicipalityCode(code):
    return municipalityUriDf.loc[municipalityUriDf['municipalityCode.value'] == code].iloc[0]

#Add all triples of parking provider to graph
def addProviderTriples(provider):
    #Create uri of provider
    providerUri = URIRef(pns + "C" + provider["organisasjonsnummer"])

    #Create URIs of external resources
    municipalityCode = getMunicipalityCodeFromPostal(provider["postnummer"])
    locationInfo = getLocationUrisFromMunicipalityCode(municipalityCode)
    municipalityIri = URIRef(locationInfo["municipality.value"])
    countyIri = URIRef(locationInfo["county.value"])
    countryIri = URIRef(locationInfo["country.value"])
    org_number_propIri = URIRef("https://www.wikidata.org/wiki/Property:P2333")

    #Add triples to graph
    g.add( ( providerUri, RDF.type, pns.ParkingCompany ) )
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

#Add triples for parking facility to graph
def addFacilityTriples(facility):
    #Create uri of facility
    facilityUri = URIRef(pns + "F" + str(facility["id"]))

    #Create URIs of external resources
    municipalityCode = getMunicipalityCodeFromPostal(facility["aktivVersjon"]["postnummer"])
    providerUri = URIRef(pns + "C" + facility["parkeringstilbyderOrganisasjonsnummer"])
    locationInfo = getLocationUrisFromMunicipalityCode(municipalityCode)
    municipalityIri = URIRef(locationInfo["municipality.value"])
    countyIri = URIRef(locationInfo["county.value"])
    countryIri = URIRef(locationInfo["country.value"])

    #Add triples to graph
    g.add( ( facilityUri, pns.operated_by, providerUri) )
    g.add( ( facilityUri, RDFS.label, Literal( facility["aktivVersjon"]["navn"]) ) )

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

    #Some characters from the handicap description inxludes illegal XML characters. We use a regex to remove these characters.
    filteredHandicapInformation = illegalXmlCharactersRegex.sub('', str(facility["aktivVersjon"]["vurderingForflytningshemmede"]))

    if (filteredHandicapInformation != "None"):
        g.add( ( facilityUri, pns.handicap_information, Literal( filteredHandicapInformation, lang="no") ) )


    g.add( ( facilityUri, geo.lat, Literal(facility['breddegrad'], datatype=XSD.float)) )
    g.add( ( facilityUri, geo.long, Literal(facility['lengdegrad'], datatype=XSD.float)) )
    g.add( ( facilityUri, wikiprop.P625, Literal( f"Point({facility['lengdegrad']} {facility['breddegrad']})", datatype=geo.wktLiteral ) ) )

    g.add( ( facilityUri, pns.activation_date, Literal( facility["aktivVersjon"]["aktiveringstidspunkt"], datatype=XSD.dateTime ) ) )

    if(facility["deaktivert"] != None):
        g.add( ( facilityUri, pns.deactivation_date, Literal( facility["deaktivert"]["deaktivertTidspunkt"], datatype=XSD.dateTime ) ) )
        g.add( (facilityUri, pns.active, Literal( False ) ) )
    else:
        g.add( (facilityUri, pns.active, Literal( True ) ) )


    #Add comments in both english and norwegian.
    commentEn = str(facility["aktivVersjon"]["navn"]) + " is a "
    commentNo = str(facility["aktivVersjon"]["navn"]) + " er "

    #We need to translate the JSON tags to the english classes ParallelParking, ParkingLot and ParkingGarage.
    parkingType = facility["aktivVersjon"]["typeParkeringsomrade"]
    if (parkingType == "LANGS_KJOREBANE"):
        g.add( (facilityUri, RDF.type, pns.ParallelParking) )
        commentEn += "parallel parking place"
        commentNo += "en gateparkering"
    elif (parkingType == "AVGRENSET_OMRADE"):
        g.add( (facilityUri, RDF.type, pns.ParkingLot) )
        commentEn += "parking lot"
        commentNo += "en parkeringsplass"
    elif (parkingType == "PARKERINGSHUS"):
        g.add( (facilityUri, RDF.type, pns.ParkingGarage) )
        commentEn += "parking garage"
        commentNo += "et parkeringshus"

    commentEn += " in Norway."
    commentNo += " i Norge."
    g.add( ( (facilityUri, RDFS.comment, Literal(commentEn, lang="en") ) ) )
    g.add( ( (facilityUri, RDFS.comment, Literal(commentNo, lang="no") ) ) )


#Generates the ontology with RDF triples
def addOntology():
    #Create the URI for the attribute where pns is the namespace for http://norpark.ml
    uri = URIRef(pns + "operated_by")
    g.add( (uri, RDF.type, RDF.Property ) )
    g.add( (uri, RDFS.label, Literal("is operated by", lang="en") ) )
    g.add( (uri, RDFS.comment, Literal("A parking facility is operated by a parking company.", lang="en") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, URIRef(pns + "ParkingCompany") ) )
    g.add( (uri, RDFS.subClassOf, URIRef("http://schema.mobivoc.org/#operatedBy") ) )


    uri = URIRef(pns + "active")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("active", lang="en") ) )
    g.add( (uri, RDFS.comment, Literal("Tells if the parking facility is active or not.", lang="en") ) )
    g.add( (uri, RDFS.range, XSD.boolean) )


    uri = URIRef(pns + "deactivation_date")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("deactivation date", lang="en") ) )
    g.add( (uri, RDFS.comment, Literal("The date the Parking facility was deactivated.", lang="en") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.dateTime) )


    uri = URIRef(pns + "activation_date")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("activation date", lang="en") ) )
    g.add( (uri, RDFS.comment, Literal("The date the Parking facility was activated.", lang="en") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.dateTime) )


    uri = URIRef(pns + "handicap_information")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("handicap information", lang="en") ) )
    g.add( (uri, RDFS.comment, Literal("Handicap information for the parking facility.", lang="en") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.string) )


    uri = URIRef(pns + "no_of_parking_spaces_without_fee")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("number of parking spaces without fee", lang="en") ) )
    g.add( (uri, RDFS.comment, Literal("Number of parking spaces without a fee.", lang="en") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.integer) )


    uri = URIRef(pns + "no_of_parking_spaces_with_fee")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("number of parking spaces with fee", lang="en") ) )
    g.add( (uri, RDFS.comment, Literal("Number of parking spaces with a fee.", lang="en") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.integer) )


    uri = URIRef(pns + "no_of_handicap_parking_spaces")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("number of handicap parking spaces.", lang="en") ) )
    g.add( (uri, RDFS.comment, Literal("Number of handicap parking spaces.", lang="en") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.integer) )


    uri = URIRef(pns + "no_of_electric_vehicle_chargers")
    g.add( (uri, RDF.type, RDFS.Datatype) )
    g.add( (uri, RDFS.label, Literal("number of electric vehicle chargers", lang="en") ) )
    g.add( (uri, RDFS.comment, Literal("Number of electric vehicle chargers available at the parking facility.", lang="en") ) )
    g.add( (uri, RDFS.domain, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.range, XSD.integer) )


    uri = URIRef(pns + "ParkingCompany")
    g.add( (uri, RDF.type, RDFS.Class) )
    g.add( (uri, RDFS.subClassOf, URIRef("http://schema.mobivoc.org/#Organization") ) )


    uri = URIRef(pns + "ParkingFacility")
    g.add( (uri, RDF.type, RDFS.Class) )
    g.add( (uri, RDFS.subClassOf, URIRef("http://schema.mobivoc.org/#ParkingFacility") ) )


    uri = URIRef(pns + "ParkingLot")
    g.add( (uri, RDF.type, RDFS.Class) )
    g.add( (uri, RDFS.subClassOf, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.subClassOf, URIRef("http://schema.mobivoc.org/#ParkingLot") ) )


    uri = URIRef(pns + "ParkingGarage")
    g.add( (uri, RDF.type, RDFS.Class) )
    g.add( (uri, RDFS.subClassOf, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.subClassOf, URIRef("http://schema.mobivoc.org/#ParkingGarage") ) )


    uri = URIRef(pns + "ParallelParking")
    g.add( (uri, RDF.type, RDFS.Class) )
    g.add( (uri, RDFS.subClassOf, URIRef(pns + "ParkingFacility") ) )
    g.add( (uri, RDFS.subClassOf, URIRef(pns + "ParallelParking") ) )


def fillGraph(parkDict):
    #For every parking provider, generate RDF triples for it.
    for v in parkDict:
        addProviderTriples(v)
        #For every parking facility the parking provider has, generate RDF triples for it.
        for i in v["parkeringsomrader"]:
            addFacilityTriples(i)

def transform():
    fillPostalDf()
    fillMunicipalityUriDf()
    parkDict = getParkingDict()

    print("Adding ontology..")
    addOntology()
    print("Adding entities..")
    fillGraph(parkDict)

    #Create the file path for the rdf file.
    rdfPath = str(pathlib.Path(__file__).parent.resolve()) + "/../data/parking.rdf"
    g.serialize(destination=rdfPath, format="xml")
    #Change permissions so that airflow is able to access the file.
    os.chmod(rdfPath, stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    print("Done!")

if __name__ == '__main__':
    transform()
