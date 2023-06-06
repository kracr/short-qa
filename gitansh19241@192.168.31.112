from helpers.answer_question import answer_question
from flask import Flask, request
import nltk

app = Flask(__name__)


@app.route("/<question>")
def hello_world(question):
    # nltk.download('omw-1.4')
    answer = answer_question(question)
    if answer == None:
        return ''
    if len(answer) > 0 and type(answer[0]) == tuple:
        answer = (answer[0][2][answer[0][2].find(':') + 2:])
    if type(answer) == list and type(answer[0]) == str:
        answer = answer[0]
    # print('key',answer)
    return {"answer": answer}


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)

hello_world("What was Guatama Buddha's father's name?")
hello_world("What are the Four noble truths?")
hello_world("Who is Gautam Buddha?")
