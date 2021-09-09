
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
  print(r)
  data = r.json()
  print(json.dumps(data, indent=4))

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

q3 = """
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

DESCRIBE <http://tisk.ml/data/parking#C930475610>
"""


q4 = '''
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


SELECT ?place ?location 
WHERE
{
  SERVICE <http://query.wikidata.org/sparql>
  {
    wd:Q62266 wdt:P625 ?ålesundloc .
  }
  <http://tisk.ml/data/parking#F948> wdt:P625 ?location

  SERVICE <http://query.wikidata.org/sparql>
  {
  SERVICE wikibase:around {
  ?place wdt:P625 ?location .
  bd:serviceParam wikibase:center ?ålesundloc .
  bd:serviceParam wikibase:radius "100" .
  }
  }
} LIMIT 50
'''

  # SERVICE <http://query.wikidata.org/sparql>
  # {
  #   } .
  # }






q5 = '''
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
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX spatial: <http://jena.apache.org/spatial#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>

SELECT ?place ?location
WHERE
{
  ?place (wdt:P625) ?location .

} LIMIT 50
# # '''

  #?place ?l ?location .
  # ?location geof:isValid ?spatialObject2.
  # <http://tisk.ml/data/parking#F948> wdt:P625 ?location .
  # SERVICE <http://query.wikidata.org/sparql>
  # {
  #   wd:Q62266 wdt:P625 ?ålesundloc .
  # }
  # ?place spatial:nearby(?lat ?lon ?radius [ ?unitsURI [ ?limit]])

  # ?place wdt:P625 ?location .
  # bd:serviceParam wikibase:center ?ålesundloc .
  # bd:serviceParam wikibase:radius "100" .
  # }
  # }
# } LIMIT 50

query(q5)
