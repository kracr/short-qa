# import grequests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pickle


class EntityExtractor:

    VALID_URL_START = "/wiki/"
    URL_PREFIX = "https://en.wikipedia.org"
    SAVE_PATH = "./reqrelevant_entities.pkl"

    @staticmethod
    def handle_exception(*args):
        print(f"Request fail ⚠️:", *args)

    @staticmethod
    def get_links_from_soup(soup, filter):
        return [
            link.get("href") for link in soup.findAll("a") if filter(link.get("href"))
        ]

    @staticmethod
    def get_entity_id(url):
        if type(url) != str or not url:
            return None

        entity_id = url.split("/")[-1]
        if len(entity_id) <= 1 or entity_id[0] != "Q" or not entity_id[1:].isnumeric():
            return None
        return entity_id

    @staticmethod
    def get_entity_data_from_html(html):
        soup = BeautifulSoup(html, "html.parser")
        links = EntityExtractor.get_links_from_soup(
            soup, lambda link: EntityExtractor.get_entity_id(link) is not None
        )
        id = EntityExtractor.get_entity_id(links[0]) if len(links) > 0 else None
        name = soup.select("#firstHeading")
        name = name[0].text if len(name) > 0 else None
        return id, name

    @classmethod
    def is_valid_entity_url(cls, url):
        if type(url) != str or not url:
            return False
        url = url.strip().lower()
        return (
            url[: len(cls.VALID_URL_START)] == cls.VALID_URL_START
            and url[len(cls.VALID_URL_START) :].find(":") == -1
        )

    def __init__(self):
        self.entities = {}
        self.explored_links = set()

    def get_links(self, url):
        wiki_html = grequests.map((grequests.get(url),))

        wiki_html = wiki_html[0]
        wiki_html = wiki_html.content.decode("UTF-8")

        soup = BeautifulSoup(wiki_html, "html.parser")
        links = [
            f"{EntityExtractor.URL_PREFIX}{link}"
            for link in EntityExtractor.get_links_from_soup(
                soup, EntityExtractor.is_valid_entity_url
            )
        ]
        pre_filter_links = len(links)
        links = [link for link in links if link not in self.explored_links]
        print(f"Found {len(links)} links ({pre_filter_links} total pre-filtering) 🔗")
        self.explored_links.update(links)

        return links

    def __call__(self, url: str) -> None:
        print(f"\nStarting extraction for '{url}' 🔭")

        links = self.get_links(url)
        reqs = [grequests.get(link) for link in links]
        # reqs = [requests.get(link) for link in links]

        none_found, total_found = 0, 0
        for resp in tqdm(
            grequests.imap(
                reqs, size=40, exception_handler=EntityExtractor.handle_exception
            ),
            unit="req",
            total=len(reqs),
        ):
            if resp is None:
                continue

            id, name = EntityExtractor.get_entity_data_from_html(
                resp.content.decode("UTF-8")
            )
            if id is None:
                none_found += 1
            total_found += 1
            self.entities[name] = id

        print(
            f"Extracted {total_found} entity IDs : {none_found} are null {'😅' if none_found == 0 else '😭' }"
        )

    def save(self, save_path=None) -> None:
        path = EntityExtractor.SAVE_PATH if save_path is None else save_path

        try:
            with open(path, "wb") as file:
                pickle.dump(self.entities, file)
            print(
                f"\nSuccessfully saved {len(self.entities)} entities  to '{path}' 🎉🎉🎉"
            )
        except:
            print(f"\nFailed to save entities to '{path}' ⛔️⛔️⛔️")

    def save_ids(self, save_path):
        with open(save_path, "w") as file:
            file.writelines(
                [
                    self.entities[ent] + "\n"
                    for ent in self.entities
                    if ent and self.entities[ent]
                ]
            )

    def load(self, save_path=None) -> dict:
        path = EntityExtractor.SAVE_PATH if save_path is None else save_path
        entities_on_disk = None
        try:
            with open(path, "rb") as file:
                entities_on_disk = pickle.load(file)
        except Exception as err:
            print(err)
            print(f"Failed to load saved entities from '{path}' ⛔️")

        self.entities = entities_on_disk
        self.explored_links.update(self.entities.keys())
        return self.entities
