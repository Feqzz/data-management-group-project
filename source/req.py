import requests

url = 'https://query.wikidata.org/sparql'
query = '''
PREFIX p1: <http://www.wikidata.org/prop/>
PREFIX ps1: <http://www.wikidata.org/prop/statement/>
    SELECT DISTINCT ?item WHERE {
      ?item p1:P2504 ?statement0.
      ?statement0 (ps1:P2504) "1507".
    }
    LIMIT 100
'''

r = requests.get(url, params = {'format': 'json', 'query': query})
data = r.json()
print(data)
