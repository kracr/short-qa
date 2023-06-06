from helpers.preprocess import *
from helpers.wikidata_helper import get_entity_description, get_entity_type
import re
import wikidata.client
import pickle
import spacy
nlp = spacy.load("en_core_web_sm")


client = wikidata.client.Client()

properties = pickle.load(file=open("data/properties", "rb"))
properties_of_ent = pickle.load(file=open("data/properties_of_ent", "rb"))

describe_ent_question = re.compile(
    r"@<((THING)|(PERSON))> ((was)|(is)|(are))( (a)|(the))? @<(?P<entity>Q[0-9]*)>[ \?]*"
)
simple_question = re.compile(
    r"@<(?P<type>(PERSON)|(DATETIME)|(LOC))>(.(?<!@))*@<(?P<entity>Q[0-9]*)>((?!@).)*"
)
entities = re.compile(r"@<(?P<entity>Q[0-9]*)>")
question_type = re.compile(r"@<(?P<type>[A-Z]*)>")


def is_candidate(question, triple):
    bag_of_words_query = get_bag_of_words_query(question)
    bag_of_words_triple = get_bag_of_words_triple(triple)
    count = len(bag_of_words_query.intersection(bag_of_words_triple))
    return count


def find_candidates(question, preprocessed_question):
    candidates = []

    entity_list = entities.findall(preprocessed_question)

    for entity in entity_list:
        if entity not in properties_of_ent:
            print("NEW ENTITY ENCOUNTERED: ", entity)
            return []
        for triple in properties_of_ent[entity]:
            score = is_candidate(question, triple)
            if score > 0:
                if str(triple[2])[0] == "Q":
                    answer = str(client.get(triple[2]).label)
                    # print('Hello',triple,str(client.get(triple[0]).label))
                    answer_type = get_entity_type(triple[2])
                    candidates.append(
                        (score, triple, properties[triple[1]]["label"] + " : " + answer)
                    )
                else:
                    answer = str(triple[2])
                    if 'wikidata' in answer:
                        answer=re.findall("\d+\.\d+",answer)[0]
                    candidates.append(
                        (score, triple, properties[triple[1]]["label"] + " : " + answer)
                    )
        candidates.sort(reverse=True)
    # for i in range(len(candidates)):
    #     print('Candidate',i,candidates[i])
    return candidates


def find_exact_answer(question, preprocessed_question, candidates):
    if len(candidates) == 0:
        return None
    shortlisted_candidates = []
    for candidate in candidates:
        verbs = get_lemmatized_verbs(question)
        bow_triple = get_bag_of_words_triple(candidate[1])
        common_verbs = bow_triple.intersection(verbs)
        if len(common_verbs) >= 1 or candidate[0] >= 2:
            shortlisted_candidates.append(candidate)
    return shortlisted_candidates

def remove_apostrophe(lst):
    lst1=[]
    # print(lst)
    for i in range(len(lst) - 1, 0, -1):
        if lst[i][0] == "'s":
            # print('hile')
            j = i - 1
            while lst[j][1] in ['PROPN', 'NOUN', 'PART']:
                j -= 1
            # print(lst[:j + 1])
            lst1 = lst[:j + 1] + [(lst[i + 1][0] + ' of', lst[i + 1][1])] + lst[j + 1:i] + lst[i + 2:]
            break
    q=''
    for i in lst1:
        q+=i[0]+' '
    return lst1,q
def answer_question(question):
    answers = []

    question = question.replace("?", "")
    question = question.replace("’", "'")
    question = question.replace("which year", "when")
    question = question.replace("Which year", "when")

    while "'s" in question:
        lst = []
        doc = nlp(question)
        for token in doc:
            lst.append((token.text, token.pos_))
        lst,question=remove_apostrophe(lst)
        question = question.replace(" 's", "'s")
    countN=[]
    doc = nlp(question)
    for token in doc:
        if token.pos_=='NOUN':
            countN.append((token.text, token.pos_))
    blocker=''
    if len(countN)>1:
        blocker=countN[0][0]
    preprocessed_question,flag = preprocess_question(question)
    if flag==1:
        question = question.replace("where", "which place")
        question = question.replace("Where", "which place")
    # print(question)
    # print(preprocessed_question)
    if not preprocessed_question:
        return None

    is_describe_ent_question = describe_ent_question.fullmatch(preprocessed_question)
    if is_describe_ent_question:
        answers.append(
            str(get_entity_description(is_describe_ent_question.group("entity")))
        )
        return answers

    question_type_list = question_type.findall(preprocessed_question)
    if not question_type_list:
        question_type_list = ["THING"]

    candidates = find_candidates(question, preprocessed_question)
    final_ans = find_exact_answer(question, preprocessed_question, candidates)

    if final_ans==[]:
        if len(candidates)==1:
            return candidates
        else:
            ans=[]
            for c in candidates:
                if '@<DATETIME>' in preprocessed_question:
                    if 'date' in c[2] or 'time' in c[2] or 'inception' in c[2]:
                        ans.append(c)
                elif '@<LOC>' in preprocessed_question:
                    if 'location' in c[2] or 'place' in c[2]:
                        ans.append(c)
                else:
                    if 'date' in c[2] or 'time' in c[2] or 'inception' in c[2] or 'location' in c[2] or 'place' in c[2]:
                        pass
                    elif blocker!='':
                        if blocker in c[2]:
                            pass
                        else:
                            ans.append(c)
                    else:
                        ans.append(c)
            return ans
    if final_ans!=None and len(final_ans)>0:
        ans = []
        for c in candidates:
            if '@<DATETIME>' in preprocessed_question:
                if 'date' in c[2] or 'time' in c[2] or 'inception' in c[2]:
                    ans.append(c)
            elif '@<LOC>' in preprocessed_question:
                if 'location' in c[2] or 'place' in c[2]:
                    ans.append(c)
            else:
                if 'date' in c[2] or 'time' in c[2] or 'inception' in c[2] or 'location' in c[2] or 'place' in c[2]:
                    pass
                elif blocker != '':
                    if blocker in c[2]:
                        pass
                    else:
                        ans.append(c)
                else:
                    ans.append(c)
        if len(ans)>0:
            return ans
    return final_ans
