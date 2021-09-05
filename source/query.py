
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
#from Wikidata
def query(q):
  url = 'http://tisk.ml:3030/parking/query'
  # print(q)
  r = requests.get(url, params = {'format': 'json', 'query': q})
  # print(r)
  data = r.json()

  df = pd.json_normalize(data["results"]["bindings"])
  print(df)


q1 = '''
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
PREFIX SDO: <http://schema.org/>

SELECT ?name ?lab
WHERE
{
  ?name SDO:PostalAddress ?a.
  ?a SDO:postalCode "6004".
  ?name rdfs:label ?lab
} LIMIT 50
# # '''

q2 = '''
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
PREFIX SDO: <http://schema.org/>


SELECT ?name ?lab ?fylke
WHERE
{
  ?name SDO:PostalAddress ?a.
  ?a SDO:postalCode "6003".
  ?name rdfs:label ?lab .
  ?a SDO:addressRegion ?d .
   SERVICE <http://query.wikidata.org/sparql>
   {
      ?d rdfs:label ?fylke
      FILTER (lang(?fylke) = 'en' || lang(?fylke) = 'ar')
   }
} LIMIT 50
# # '''

query(q2)
