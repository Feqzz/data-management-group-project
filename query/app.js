
var yasgui = YASGUI(document.getElementById("yasgui"), {
	yasqe:{
		value: "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
			"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
	 		"PREFIX geo: <http://www.opengis.net/ont/geosparql#>\n" +
			"PREFIX norpark: <http://norpark.ml/>\n" +
			"PREFIX wikiprop: <https://www.wikidata.org/wiki/Property:>\n" +
			"PREFIX schema: <http://schema.org/>\n" +
			"SELECT ?sub ?lab ?wkt ?wktLabel WHERE\n" +
			"{\n" +   
				"?sub rdf:type norpark:ParkingFacility .\n" +  
				"?sub rdfs:label ?lab .\n" +  
				"?sub wikiprop:P625 ?wkt .\n" +
				"?sub schema:PostalAddress ?addr .\n" +
				"?addr schema:postalCode ?postalCode .\n" +
				"FILTER(?postalCode = \"3016\") .\n" +
			"}\n" +  
			"LIMIT 10",
		sparql:{
			endpoint:'http://data.norpark.ml/dataset/sparql'
		}
	}
});

