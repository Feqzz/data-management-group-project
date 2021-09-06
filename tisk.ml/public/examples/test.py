from owlready2 import *

onto = get_ontology("http://tisk.ml/examples/myontology")

class ParkingArea(Thing):
    namespace = onto

class ParkingProvider(Thing):
    namespace = onto


stromso = ParkingArea("stromso")
stromso.label = "Strømsø"
print(stromso.name)
print(stromso.iri)


onto.save(file = "myontology.rdf", format = "rdfxml")


