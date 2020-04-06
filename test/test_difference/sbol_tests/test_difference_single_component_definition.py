import sbol

def test1():
    sbol.setHomespace('http://sbol_prefix.org') 
    doc = sbol.Document()
    
    pTetR = sbol.ComponentDefinition("test_promoter_1", sbol.BIOPAX_DNA)
    pTetR.roles = sbol.SO_PROMOTER
    doc.addComponentDefinition(pTetR)

    results = doc.write("pysbol_output.xml")
    return results


def main():
    test1()


if __name__ == "__main__":
    main()