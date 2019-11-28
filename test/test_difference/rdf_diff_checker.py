import sys
import rdflib
import rdflib.compare

def rdf_difference_check(file1,file2):
    g1 = rdflib.Graph()
    g1.load(file1)
    iso1 = rdflib.compare.to_isomorphic(g1)
    g2 = rdflib.Graph()
    g2.load(file2)
    iso2 = rdflib.compare.to_isomorphic(g2)
    rdf_diff = rdflib.compare.graph_diff(iso1, iso2)
    if rdf_diff[1] or rdf_diff[2]:
        print('Detected %d differences in RDF', len(rdf_diff[1]) + len(rdf_diff[2]))
        print("Difference in File1: ")
        for stmt in rdf_diff[1]:
            print(stmt)
        for stmt in rdf_diff[2]:
            print('Only in loaded: %r', stmt)
    else:
        print("No Difference Found")

if __name__ == "__main__":
    rdf_difference_check(sys.argv[1],sys.argv[2])