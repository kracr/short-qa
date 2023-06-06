import wikidata.client
from SPARQLWrapper import SPARQLWrapper, JSON
import sys

endpoint_url = "https://query.wikidata.org/sparql"
client = wikidata.client.Client()

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def get_entity_type(ent_id):
    type_query = 'SELECT ?class WHERE { \
        wd:' + str(ent_id) + ' wdt:P31 ?item. \
        ?item wdt:P279* ?class. \
        VALUES ?class {  wd:Q17334923 wd:Q5 wd:Q4271324 } \
    }'
    results = get_results(endpoint_url, type_query)['results']['bindings']
    if len(results) > 0:
        ent_type = results[0]['class']['value'][31:]
        if ent_type == 'Q5' or ent_type == 'Q4271324':
            return 'PERSON'
        elif ent_type == 'Q17334923':
            return 'LOC'
        else:
            return 'THING'

def get_entity_description(ent_id):
    entity = client.get(ent_id, load = True)
    return entity.description
