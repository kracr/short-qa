import wikidata.client, wikidata.entity
from tqdm import tqdm
import datetime

client = wikidata.client.Client()

with open('data/doc_entities.txt') as file:
    text = file.readlines()
def standarised_date(date_str) :
    date_str = date_str.strip()
    date=''
    monthInt = 1;
    if(date_str[9:11]!='00'):
        date+=date_str[9:11]+' '
    if(date_str[6:8]!='00'):
        month = datetime.date(1900, int(date_str[6:8]), 1).strftime('%B')
        date+=month+' '
    date += date_str[1:5]
    if date_str[0] == '-' :
        date += ' BC'
    return date
edges = []
entities = set([])
for line in tqdm(text):
    entity_id = line.strip()
    entities.add(entity_id)
    entity = client.get(entity_id, load=True)
    for property in entity.keys():
        if property.id=='P106':
            print(entity.id,property.id, entity[property].id, entity.attributes['claims'][property.id])
            # for k in entity[property]:
            #     print(k)
        try:
            if entity[property].__class__ is wikidata.entity.Entity:

                edge = (entity.id, property.id, entity[property].id)
            else:
                edge = (entity.id, property.id, entity[property])
            # print(property.id)
            edges.append(edge)
            entities.add(edge[2])
        except:
            # print(property.id)
            try:
                edges.append((entity.id, property.id,standarised_date(entity.attributes['claims'][property.id][0]['mainsnak']['datavalue']['value']['time'])))
            except:
                edges.append((entity.id, property.id, 'not_downloaded'))
            # print(entity.attributes['claims'][property.id][0]['mainsnak']['datavalue']['value']['time'],standarised_date(entity.attributes['claims'][property.id][0]['mainsnak']['datavalue']['value']['time']))
            # edges.append((entity.id, property.id, 'not_downloaded'))

# file = open('data/subgraph.txt', 'w', encoding='utf8')
# for edge in edges:
#     print(edge, file=file)
# file.close()