import sbol

def test1():
    sbol.setHomespace('http://sbol_prefix.org') 
    doc = sbol.Document()
    
    pTetR = sbol.ComponentDefinition("pTetR", sbol.BIOPAX_DNA)
    pTetR.roles = sbol.SO_PROMOTER
    doc.addComponentDefinition(pTetR)

    lacI_CDS = sbol.ComponentDefinition("target", sbol.BIOPAX_DNA)
    lacI_CDS.roles = sbol.SO_CDS
    doc.addComponentDefinition(lacI_CDS)


    results = doc.write("output_sbol.xml")
    return results


def main():
    test1()


if __name__ == "__main__":
    main()