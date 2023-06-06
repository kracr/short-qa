from helpers.entity_extractor import EntityExtractor

urls = [
    "https://en.wikipedia.org/wiki/Humayun",
    "https://en.wikipedia.org/wiki/Humayun%27s_Tomb",
    "https://en.wikipedia.org/wiki/Mughal_Empire",
]
extractor = EntityExtractor()

for url in urls:
    extractor(url)

extractor.save(save_path="./data/humayun_entities.pkl")
entities = extractor.load(save_path="./data/humayun_entities.pkl")

print()
for name, id in entities.items():
    print(f"{name}: {id}")
