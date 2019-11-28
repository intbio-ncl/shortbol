import sbol

def crispr_tutorial_short():
    sbol.setHomespace('http://sbols.org/CRISPR_Example') 
    doc = sbol.Document()
    
    target_gene = sbol.ComponentDefinition("target_gene", sbol.BIOPAX_DNA)
    target_gene.roles = sbol.SO_PROMOTER
    doc.addComponentDefinition(target_gene)
    target = sbol.ComponentDefinition("target", sbol.BIOPAX_PROTEIN)
    doc.addComponentDefinition(target)


    CRISPR_Template = sbol.ModuleDefinition("CRISPR_Template")
    doc.addModuleDefinition(CRISPR_Template)



    target_gene_fc = CRISPR_Template.functionalComponents.create("target_gene_fc")
    target_gene_fc.definition = target_gene.identity
    target_gene_fc.access = sbol.SBOL_ACCESS_PUBLIC
    target_gene_fc.direction = sbol.SBOL_DIRECTION_IN_OUT

    target_fc = CRISPR_Template.functionalComponents.create("target_fc")
    target_fc.definition = target.identity
    target_fc.access = sbol.SBOL_ACCESS_PUBLIC
    target_fc.direction = sbol.SBOL_DIRECTION_IN_OUT
    
    
    target_generic_gene_inhibition = CRISPR_Template.interactions.create("target_gene_inhibition_interaction")
    target_generic_gene_inhibition.types = sbol.SBO_GENETIC_PRODUCTION
    target_gene_participation = target_generic_gene_inhibition.participations.create("target_gene_participation")
    target_gene_participation.roles = sbol.SBO_PROMOTER
    target_gene_participation.participant = target_gene_fc.identity
    target_participation = target_generic_gene_inhibition.participations.create("target_participation")
    target_participation.roles = sbol.SBO_PRODUCT
    target_participation.participant = target_fc.identity




    gRNA_gene = sbol.ComponentDefinition("gRNA_gene",sbol.BIOPAX_DNA)
    gRNA_gene.roles = sbol.SO_PROMOTER
    doc.addComponentDefinition(gRNA_gene)
    gRNA_b = sbol.ComponentDefinition("gRNA_b",sbol.BIOPAX_RNA)
    gRNA_b.roles = sbol.SO_SGRNA
    doc.addComponentDefinition(gRNA_b)

    CRPb_circuit = sbol.ModuleDefinition("CRPb_characterization_Circuit")
    doc.addModuleDefinition(CRPb_circuit)
    
    gRNA_b_fc = CRPb_circuit.functionalComponents.create("gRNA_b_fc")
    gRNA_b_fc.definition = gRNA_b.identity
    gRNA_b_fc.access = sbol.SBOL_ACCESS_PUBLIC
    gRNA_b_fc.direction = sbol.SBOL_DIRECTION_NONE
    gRNA_b_fc.version = 1
    gRNA_gene_fc = CRPb_circuit.functionalComponents.create("gRNA_gene_fc")
    gRNA_gene_fc.definition = gRNA_gene.identity
    gRNA_gene_fc.access = sbol.SBOL_ACCESS_PUBLIC
    gRNA_gene_fc.direction = sbol.SBOL_DIRECTION_NONE
    gRNA_gene_fc.version = 1



    gRNA_b_production = CRPb_circuit.interactions.create("gRNA_b_production")
    gRNA_b_production.types = sbol.SBO_GENETIC_PRODUCTION
    gRNA_b_gene_participant = gRNA_b_production.participations.create("gRNA_b_gene")
    gRNA_b_gene_participant.roles = sbol.SBO_PROMOTER
    gRNA_b_gene_participant.participant = gRNA_gene_fc.identity
    gRNA_b_participant = gRNA_b_production.participations.create("gRNA_b")
    gRNA_b_participant.roles = sbol.SBO_PRODUCT
    gRNA_b_participant.participant = gRNA_b_fc.identity
    

    gRNA_b_BFP_deg = CRPb_circuit.interactions.create("gRNA_b_BFP_deg")
    gRNA_b_BFP_deg.types = sbol.SBO_DEGRADATION
    gRNA_b_BFP_participant = gRNA_b_BFP_deg.participations.create("gRNA_b_BFP")
    gRNA_b_BFP_participant.roles = sbol.SBO_REACTANT
    gRNA_b_BFP_participant.participant = gRNA_b_fc.identity



    Template_Module = CRPb_circuit.modules.create("CRISPR_Template")
    Template_Module.definition = CRISPR_Template.identity

    gRNA_b_map = Template_Module.mapsTos.create("gRNA_b_map")
    gRNA_b_map.refinement = sbol.SBOL_REFINEMENT_USE_LOCAL
    gRNA_b_map.local = gRNA_b_fc.identity
    gRNA_b_map.remote = gRNA_gene_fc.identity
    gRNA_b_map.name = "Hnelo"


    results = doc.write("CRISPR_example_short_2.xml")
    print(results)


def main():
    crispr_tutorial_short()


if __name__ == "__main__":
    main()