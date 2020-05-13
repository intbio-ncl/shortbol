The standard template library for ShortBOL is created in increasing layer of abstraction where the lowest number is essentially 
the raw SBOL data models and highest numbers are abstractions.

Higher Layers are still SBOL compliant but are more intuitive and can be understood by users coming from purely biological backgrounds.

We have tried to make each layer distinct that follow a consistent and standard interface allowing multiple ways of writing ShortBOL.

It is advised to not use templates from different modes where possible as this could result in unintuitive ShortBOL.


-Developer Mode
The first layer implemented when ShortBOL was first created.
This layer is almost a direct relation with the SBOL data model.
This template can be used by users that understand and are happy with a precise but verbose language and that understand the SBOL Data Model well, specifically how different types interact.

-User Mode
User Mode allows reduces the knowledge requirement of SBOL and allows quicker and more intuative development of SBOL designs.
This means that when you create an instance of these templates, behind the scenes more templates are created.
This means that user created ShortBOL should be smaller and more compact and also reduced most knowledge requirement of the SBOL data model.
This template is for users that want to utilise the full power of the SBOL data model but want a shorthand and/or simplified way of using the often cumbersome and unnecessarily complicated data model.
Note: it is advised to use only the specialised templates for this layer to further increase readability of designs.












