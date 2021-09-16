
//Predefined example queries
var queries = [
	//Query 0
	"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
	"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
	"PREFIX norpark: <http://norpark.ml/>\n" +

	"SELECT ?parking ?label WHERE\n" +
	"{\n" +   
		"\t?parking a norpark:ParkingFacility .\n" +
		"\t?parking rdfs:label ?label .\n" +
	"}\n" +  
	"LIMIT 100",

	//query 1
	"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
	"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
	"PREFIX geo: <http://www.opengis.net/ont/geosparql#>\n" +
	"PREFIX norpark: <http://norpark.ml/>\n" +
	"PREFIX wikiprop: <https://www.wikidata.org/wiki/Property:>\n" +
	"PREFIX schema: <http://schema.org/>\n" +

	"SELECT ?sub ?lab ?wkt ?wktLabel WHERE\n" +
	"{\n" +   
		"\t?sub rdf:type norpark:ParkingFacility .\n" +  
		"\t?sub rdfs:label ?lab .\n" +  
		"\t?sub wikiprop:P625 ?wkt .\n" +
		"\t?sub schema:PostalAddress ?addr .\n" +
		"\t?addr schema:postalCode ?postalCode .\n" +
		"\tFILTER(?postalCode = \"3016\") .\n" +
	"}\n" +  
	"LIMIT 100",


	//Query 2
	"PREFIX wd: <http://www.wikidata.org/entity/>\n" +
	"PREFIX wds: <http://www.wikidata.org/entity/statement/>\n" +
	"PREFIX wdv: <http://www.wikidata.org/value/>\n" +
	"PREFIX wdt: <http://www.wikidata.org/prop/direct/>\n" +
	"PREFIX wikibase: <http://wikiba.se/ontology#>\n" +
	"PREFIX p: <http://www.wikidata.org/prop/>\n" +
	"PREFIX ps: <http://www.wikidata.org/prop/statement/>\n" +
	"PREFIX pq: <http://www.wikidata.org/prop/qualifier/>\n" +
	"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
	"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
	"PREFIX geo: <http://www.opengis.net/ont/geosparql#>\n" +
	"PREFIX norpark: <http://norpark.ml/>\n" +
	"PREFIX wikiprop: <https://www.wikidata.org/wiki/Property:>\n" +
	"PREFIX schema: <http://schema.org/>\n" +
	"PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n" +

	"SELECT ?parking ?electric_chargers ?handicap ?city ?wkt ?wktLabel WHERE\n" +
	"{\n" +   

		"\tSERVICE <http://query.wikidata.org/sparql>\n" +
		"\t{\n" +   
			"\t\t?city wdt:P31 wd:Q755707 .\n" +
			"\t\t?city rdfs:label ?label .\n" +
			"\t\t?city rdfs:label \"Kongsberg\"@en\n" +
			"\t\tFILTER (lang(?label) = \"en\") .\n" +
		"\t}\n" +  

		"\t?parking wikiprop:P625 ?wkt .\n" +
		"\t?parking rdf:type norpark:ParkingFacility .\n" +
		"\t?parking rdfs:label ?wktLabel .\n" +
		"\t?parking schema:PostalAddress ?a .\n" +
		"\t?a schema:addressLocality ?city .\n" +
		"\t?parking norpark:no_of_electric_vehicle_chargers ?electric_chargers .\n" +
		"\t?parking norpark:no_of_handicap_parking_spaces ?handicap .\n" +
		"\tFILTER (?handicap > 0) .\n" +
		"\tFILTER (?electric_chargers > 0) .\n" +
	"}\n" +  
	"LIMIT 100",

	//Query 3
	"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
	"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
	"PREFIX geo: <http://www.opengis.net/ont/geosparql#>\n" +
	"PREFIX norpark: <http://norpark.ml/>\n" +
	"PREFIX wikiprop: <https://www.wikidata.org/wiki/Property:>\n" +
	"PREFIX schema: <http://schema.org/>\n" +

	"SELECT ?sub ?lab ?wkt ?wktLabel WHERE {\n" +
		"\t?sub rdf:type norpark:ParkingFacility, norpark:ParkingGarage   .\n" +
		"\t?sub rdfs:label ?lab .\n" +
		"\t?sub wikiprop:P625 ?wkt .\n" +
		"\t?sub schema:PostalAddress ?addr .\n" +
		"\t?addr schema:addressRegion ?reg .\n" +
	  
		"\n\tFILTER(?reg = <http://www.wikidata.org/entity/Q5245991> ) .\n" +
	"} \n" +
	"LIMIT 25\n"
];

//Create yasgui instance
var yasgui = YASGUI(document.getElementById("yasgui"), {
	yasqe:{
		value: queries[document.getElementById("queries").value],
		sparql:{
			endpoint:'http://data.norpark.ml/dataset/sparql'
		}
	}
});


//On update of selectlist of examples, change value of yasgui query window
function update()
{
	q = document.getElementById("queries").value;
	yasgui.current().yasqe.setValue(queries[q]);
}

