
import os
import rdf_transform as rdf
import data_extraction as de
from data_extraction import createFullJsonFile

def stop_services():
    os.system("curl -u admin:password http://localhost:8080/manager/text/stop?path=/fuseki")
    os.system("curl -u admin:password http://localhost:8080/manager/text/stop?path=/lodview")

def extract_data_from_apis():
    # print("")
    de.createFullJsonFile()
def transform_data_to_lod():
    rdf.transform()
def restart_fuseki():
    os.system("curl -u admin:password http://localhost:8080/manager/text/reload?path=/fuseki")
def restart_lodview():
    os.system("curl -u admin:password http://localhost:8080/manager/text/reload?path=/lodview")


