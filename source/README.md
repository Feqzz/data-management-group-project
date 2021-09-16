As we have used Linux when creating this project, including using dependencies only available for Linux, this guide is written for Linux only:

Dependencies: 
* python3

Both the data extraction and transformation scripts are written in Python. To execute the scripts, we recommend creating a virtual environment.

Create and activate a new virtual environment `my-venv`:
$ python3 -m venv my-venv
$ source my-venv/bin/activate


To install the dependencies required to execute the Python scripts:
$ pip3 install -r requirements.txt


The JSON files that we fetch from Statens vegvesen are not complete, so we need to run a script that fetches all the information that we need and creates one large JSON file. To generate the JSON file:
$ python3 data_extraction.py


To generate the RDF triples alongside our parking ontology, run this command:
$ python3 rdf_transform.py


To setup the webpage and host the RDF triples, we have created configuration files for third party software.

The webpage is available publicly at http://norpark.ml.
This means that there is no need to setup Apache HTTP Server, Apache Fuseki, LodView and YASGUI with the configuration files.
