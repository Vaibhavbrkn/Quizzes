import json
import numpy as np
from tqdm import tqdm
import spacy
from keybert import KeyBERT
import random
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer,
)
import re
import transformers
import torch
from sense2vec import Sense2Vec

from fill import Fill
import math


class Question:
    def __init__(self, path="./s2v_reddit_2015_md/s2v_old"):
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
        model = T5ForConditionalGeneration.from_pretrained(
            'Vaibhavbrkn/question-gen')
        # vaibhavbrkn/question-gen
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        self.model = model
        self.device = device
        try:
            self.spacy = spacy.load('en_core_web_md')
        except:
            print("Downloading Spacy English model...")
            spacy.cli.download("en_core_web_md")
            self.spacy = spacy.load('en_core_web_md')
        self.sense = Sense2Vec().from_disk(path)
        self.mod = KeyBERT('distilbert-base-nli-mean-tokens')

    def __filter_keyword(self, data, ran=5):
        ap = []
        real = []
        res = re.sub(r'-', ' ', data)
        res = re.sub(r'[^\w\s\.\,]', '', res)
        for i in range(1, 4):
            ap.append(self.mod.extract_keywords(
                res, keyphrase_ngram_range=(1, i), diversity=0.7, top_n=ran*2))
        for i in range(3):
            for j in range(len(ap[i])):
                if ap[i][j][0].lower() in res.lower():
                    real.append(ap[i][j])

        real = sorted(real, key=lambda x: x[1], reverse=True)
        ap = []
        st = ""
        for i in range(len(real)):
            if real[i][0] in st:
                continue
            else:
                ap.append(real[i][0])
                st += real[i][0] + " "
            if len(ap) == ran:
                break

        doc = self.spacy(res.strip())
        second = []
        tag = []
        for i in doc.ents:
            entry = str(i.lemma_).lower()
            if i.label_ in ["ART", "EVE", "NAT", "PERSON", "GPE", "GEO", "ORG"]:
                if entry not in second:
                    second.append(entry)
                    tag.append(i.label_)

        return ap, second, tag

    def __edits(self, word):

        letters = 'abcdefghijklmnopqrstuvwxyz '
        ls = []
        for w in word.split(" "):
            splits = [(w[:i], w[i:]) for i in range(len(w) + 1)]
            deletes = [L + R[1:] for L, R in splits if R]
            transposes = [L + R[1] + R[0] + R[2:]
                          for L, R in splits if len(R) > 1]
            replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
            inserts = [L + c + R for L, R in splits for c in letters]
            ls = list(ls) + list(set(deletes + transposes + replaces + inserts))

        return ls

    def __handle2(self, ls):
        doc = self.sense.get_best_sense(ls[0])
        add = ls[1]
        if doc is None:
            return self.sense.get_best_sense(ls[1]), ls[0], True
        else:
            return doc, add, False

    def __handle3(self, ls):
        doc = self.sense.get_best_sense(" ".join(ls[:2]))
        if doc is None:
            doc = self.sense.get_best_sense(" ".join(ls[1:]))
            if doc is None:
                doc, add, pre = self.__handle2(ls[:2])
                if doc is None:
                    doc, add, pre = self.__handle2(ls[1:])
                    return doc, add, pre
                else:
                    return doc, add, pre
            else:
                return doc, ls[0], True
        else:
            return doc, ls[2], False

    def __similar(self, key, num=3):
        answer = []
        add = ""
        pre = False
        lemmas = [token.lemma_ for token in self.spacy(key)]
        ls = str(key).split(" ")
        doc = self.sense.get_best_sense(key)
        if doc is None:
            if len(ls) == 2:
                doc, add, pre = self.__handle2(ls)
            else:
                doc, add, pre = self.__handle3(ls)

        most_similar = self.sense.most_similar(doc, n=10)
        index = 0

        for i in range(10):
            ans = str(most_similar[i][0].split("|")
                      [0]).replace("_", " ").lower()
            if ans != key.lower() and ans not in answer and self.spacy(ans)[0].lemma_ not in lemmas:
                if len(add) > 0:
                    if pre:
                        ans = add + " " + ans
                    else:
                        ans = ans + " " + add
                answer.append(ans)
                index += 1
            if index == num:
                break

        return answer

    def __get_sim(self, label, n, tag):
        ogn = tag[n]
        real = label[n]
        ans = []
        ind = 0
        for i in range(len(tag)):
            if tag[i] == ogn and real != label[i]:
                ans.append(label[i])
                ind += 1
            if ind == 3:
                break

        return ans

    def __build_questions(self, data, min_question, max_question, total_min, total_max):
        list1, list2, tag = self.__filter_keyword(data, total_max)

        ap = []
        ind = 0
        answer = []
        fill_ques = []
        fill_key = []
        for key in list1:
            context = "context: " + data + " keyword: " + key
            source_tokenizer = self.tokenizer.encode_plus(
                context, max_length=512, pad_to_max_length=True, return_tensors="pt")
            outs = self.model.generate(input_ids=source_tokenizer['input_ids'].cuda(
            ), attention_mask=source_tokenizer['attention_mask'].cuda(), max_length=50)
            dec = [self.tokenizer.decode(ids) for ids in outs][0]
            st = dec.replace("<pad> ", "")
            st = st.replace("</s>", "")
            if st not in ap:
                ind += 1
                ap.append(st)
                ans = []
                ans.append(key)
                sim = self.__similar(key)
                for s in sim:
                    ans.append(s)
                answer.append(ans)
            if ind == total_min:
                break

        criteria = max_question-min_question

        le = criteria if len(list2) > criteria else len(list2)
        for i in range(le):
            n = random.randint(0, len(list2)-1)
            context = "context: " + data + " keyword: " + list2[n]
            source_tokenizer = self.tokenizer.encode_plus(
                context, max_length=512, pad_to_max_length=True, return_tensors="pt")
            outs = self.model.generate(input_ids=source_tokenizer['input_ids'].cuda(
            ), attention_mask=source_tokenizer['attention_mask'].cuda(), max_length=50)
            dec = [self.tokenizer.decode(ids) for ids in outs][0]
            st = dec.replace("<pad> ", "")
            st = st.replace("</s>", "")
            if st not in ap:
                ap.append(st)
                ans = []
                ans.append(list2[n])
                sim = self.__get_sim(list2, n, tag)
                for i in sim:
                    ans.append(i)
                if len(ans) < 4:
                    sim = self.__similar(list2[n], 4-len(ans))
                    for s in sim:
                        ans.append(s)
                answer.append(ans)

        for i in range(total_min - min_question):
            n = random.randint(0, len(ap)-1)
            fill_ques.append(ap[n]), fill_key.append(answer[n][0])
            del ap[n], answer[n]

        return ap, answer, fill_ques, fill_key

    def generate(self, text, min_mcq_question=5, max_mcq_question=8, min_fill_ques=2, max_fill_ques=4):
        """
           Args:
            text : (obj:`str`, `required`):
                Text to generate questions
            min_mcq_question : (obj:`int`, `optional`, defaults to 5):
                Minimum number of MCQ question to generate.
            max_mcq_question : (obj:`int`, `optional`, defaults to 8):
                Maximum number of MCQ question to generate.
            min_fill_ques : (obj:`int`, `optional`, defaults to 2):
                Minimum number of Fill in the blank question to generate.
            max_fill_ques : (obj:`int`, `optional`, defaults to 4):
                Maximum number of Fill in the blank question to generate.
            
        """

        total_min = min_mcq_question + min_fill_ques
        total_max = max_mcq_question + max_fill_ques
        question, choice, fill_ques, fill_key = self.__build_questions(
            text, min_mcq_question, max_mcq_question, total_min, total_max)

        fill_question, fill_ans = Fill.generate(
            text, min_fill_ques, max_fill_ques, fill_ques, fill_key)

        return question, choice, fill_question, fill_ans
