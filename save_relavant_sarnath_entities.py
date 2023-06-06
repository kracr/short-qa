from helpers.entity_extractor import EntityExtractor

urls = [
    "https://en.wikipedia.org/wiki/Sarnath",
    "https://en.wikipedia.org/wiki/Gautama_Buddha",
    "https://en.wikipedia.org/wiki/Buddhism",
]
extractor = EntityExtractor()

for url in urls:
    extractor(url)

extractor.save("./data/sarnath_entities.pkl")

entities = extractor.load()

print()
for name, id in entities.items():
    print(f"{name}: {id}")
