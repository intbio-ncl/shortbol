The standard template library for ShortBOL is created in increasing layer of abstraction where the lowest number is essentially 
the raw SBOL data models and highest numbers are abstractions.

Higher Layers are still SBOL compliant but are more intuitive and can be understood by users coming from purely biological backgrounds.

We have tried to make each layer distinct that follow a consistent and standard interface allowing multiple ways of writing ShortBOL.

It is advised to not use templates from different layers where possible as this could result in unintuitive ShortBOL.

All subsequent layers use this layer 1 behind the scenes, so it means that when ShortBOL is executed i.e. if the intention of ShortBOL written within different layers is the same, the output will be identical.

-Layer 1
The first layer implemented when ShortBOL was first created.
This layer is almost a direct relation with the SBOL data model.
This template can be used by users that understand and are happy with a precise but verbose language and that understand the SBOL Data Model well, specifically how different types interact.

-Layer 2
This layer introduces implicit or inline templates.
These templates are defined by templates with the same name as Layer 1 templates but with the fist letter being lower case.
For example:
@@@ @@@
These are templates which introduce implicit creation of other templates.
This means that when you create an instance of these templates, behind the scenes more templates are created.
This means that user created ShortBOL should be smaller and more compact and also reduced most knowledge requirement of the SBOL data model.
This template is for users that want to utilise the full power of the SBOL data model but want a shorthand and/or simplified way of using the often cumbersome and unnecessarily complicated data model.
Note: it is advised to use only the specialised templates for this layer to further increase readability of designs.

-Layer 3
Under Development (Not Fully Implemented).
This is the layer that will begin the full transition from an abstract SBOL  data model language to a language that uses.
This layer also introduces the idea of a new set of consistent terms that are understood by biologists.











