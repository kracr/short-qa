import wikidata.client
from tqdm import tqdm
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

from .answer_question import answer_question

stopwords = stopwords.words("english")

lemmatizer = WordNetLemmatizer()
client = wikidata.client.Client()


def answer_questions(file_path):
    questions = []
    with open(file_path) as file:
        for line in file.readlines():
            proc_line = line.strip()
            if proc_line:
                questions.append(proc_line)

    for question in questions:
        answer = answer_question(question)
