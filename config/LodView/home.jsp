<%@page session="true"%><%@taglib uri="http://www.springframework.org/tags" prefix="sp"%><%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%><html version="XHTML+RDFa 1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/1999/xhtml http://www.w3.org/MarkUp/SCHEMA/xhtml-rdfa-2.xsd" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:xsd="http://www.w3.org/2001/XMLSchema#" xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:foaf="http://xmlns.com/foaf/0.1/">
	<head data-color="${colorPair}" profile="http://www.w3.org/1999/xhtml/vocab">
		<title>${results.getTitle()}&mdash;LodView</title>
		<jsp:include page="inc/header.jsp"></jsp:include>
	</head>
	<body id="top">
		<article>
			<div id="logoBanner">
				<div id="logo">
					<!-- placeholder for logo -->
				</div>
			</div>
			<header>
				<hgroup>
					<h1>
						<span>NorPark</span>
					</h1>
					<h2></h2>
				</hgroup>
				<div id="abstract">
					<div class="value">Provides Statens Vegvesen's publicly available parking data in RDF form. This project is a done as a part of the course Data Management(CS4010-1), at the University of South-Eastern Norway, fall 2021.</div>
				</div>

			</header>

			<aside class="empty"></aside>
			<div id="directs">
				<div class="value">The SPARQL endpoint can be found at <a href="http://query.norpark.ml">query.norpark.ml</a>. We have created a small schema, that expands on existing vocabularies from <a href="http://schema.org">Schema-Org</a>, and <a href="http://schema.mobivoc.org/">Schema-Mobivoc</a>.
				</div>

				<br>
				<br>
				To browse the dataset, the top level classes, of which all individuals belong, can be found here:
				<ul>
					<li><a href="http://norpark.ml/ParkingFacility.html">Parking Facilities</a></li>
					<li><a href="http://norpark.ml/ParkingCompany.html">Parking Companies</a></li>
				</ul>
				<br>
				At time of writing the dataset consists of 244325 triples, including 10646 Parking Facilities, and 258 Parking Companies. 

				<br>
				<br>
			</div>
			<div id="inverses" class="empty"></div> 
			<jsp:include page="inc/custom_footer.jsp"></jsp:include>
		</article>
		<jsp:include page="inc/footer.jsp"></jsp:include>
	</body>
</html>
