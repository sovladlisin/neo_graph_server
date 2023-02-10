




DOMAIN_ONTOLOGY = "DomainOntology"

# NAMED:
CLASS = "http://www.w3.org/2002/07/owl#Class"
CORPUS = "http://erlangen-crm.org/current/F74_Corpus"
CORPUS_RELATION = "http://erlangen-crm.org/current/P165_incorporates"
OBJECT = "http://www.w3.org/2002/07/owl#NamedIndividual"

# RELATIONS
SUB_CLASS = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
SUB_PROPERTY = "http://www.w3.org/2000/01/rdf-schema#subPropertyOf"

IDENTIFIED_BY = "http://erlangen-crm.org/current/P1_is_identified_by"
HAS_TYPE = "http://erlangen-crm.org/current/P2_has_type"

CARRIES = "http://erlangen-crm.org/current/P128_carries"

# URI
PLACE_URI = "http://erlangen-crm.org/current/E53_Place"
PERSON_URI = "http://erlangen-crm.org/current/E21_Person"
DIGITAL_CARRIER_URI = "http://erlangen-crm.org/current/F23_Digital_Carrier"
APPELATION = "http://erlangen-crm.org/current/E41_Appellation"
DEPICTS = 'http://xmlns.com/foaf/0.1/depicts'
# TYPES
STRING = "http://www.w3.org/2000/01/rdf-schema#Literal"
TEXT_TYPE = "http://erlangen-crm.org/current/F60_Text_Type"
IMAGE_TYPE = "http://erlangen-crm.org/current/F61_Image_Type"
VIDEO_TYPE = "http://erlangen-crm.org/current/F58_Video_Type"

MP4 = 'http://erlangen-crm.org/current/mp4'
TITLE = 'http://dbpedia.org/ontology/title'
# PROPERTY
# (class) <- [pr_Rel] - (new_type) - [pr_Range] -> (type)
PROPERTY_DOMAIN = "http://www.w3.org/2000/01/rdf-schema#domain"
PROPERTY_URI = "https://www.geonames.org/ontology#" 
PROPERTY_RANGE = "http://www.w3.org/2000/01/rdf-schema#range"
LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
PROPERTY_LABEL = "http://www.w3.org/2002/07/owl#DatatypeProperty"
PROPERTY_LABEL_OBJECT = "http://www.w3.org/2002/07/owl#ObjectProperty"
NOTE_URI = "http://erlangen-crm.org/current/P3_has_note"

# workspace
HAS_TRANSLATION = "http://erlangen-crm.org/current/P73_has_translation"
IS_TRANSLATION_OF = "http://erlangen-crm.org/current/P73i_is_translation_of"
HAS_COMMENTARY = "http://erlangen-crm.org/current/R_131_has_extra_materials"

RESOURCE_NAMESPACE = "http://erlangen-crm.org/current"

VISUAL_ITEM = "http://erlangen-crm.org/current/E36_Visual_Item"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

LING_OBJECT = "http://erlangen-crm.org/current/E33_Linguistic_Object"
LANGUAGE = "http://erlangen-crm.org/current/E56_Language"
GENRE = "http://erlangen-crm.org/current/F62_Genre"

REFERS_TO = 'http://erlangen-crm.org/current/P67_refers_to'

EVENT = 'http://erlangen-crm.org/current/F8_Preparing_to_publish'
TIME = 'http://erlangen-crm.org/current/E52_Time-Span'
TIME_RELATION = 'http://erlangen-crm.org/current/P4_has_time-span'
EVENT_PERMORMED_BY = 'http://erlangen-crm.org/current/P14_carried_out_by'
EVENT_TOOK_PLACE = 'http://erlangen-crm.org/current/P7_took_place_at'