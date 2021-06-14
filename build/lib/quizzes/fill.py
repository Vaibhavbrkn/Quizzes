import pke
import re
import random


class Fill:

    def __extract(text):
        extractor = pke.unsupervised.TopicRank()
        extractor.load_document(input=text, language='en')
        extractor.candidate_selection(pos={'ADJ', 'VERB', 'NOUN'})
        extractor.candidate_weighting()
        keyphrases = extractor.get_n_best(n=40)
        keys = [k[0] for k in keyphrases]
        return keys

    def __get_sentence(text):
        sen = text.split(".")
        sentence = [s.strip() for s in sen]
        return sentence

    def __generate(se, keyphrase):
        sentence = []
        ans = []
        for s in se:
            for key in keyphrase:
                if key in s:
                    sent = re.compile(re.escape(key), re.IGNORECASE)
                    line = sent.sub(' _________ ', s)
                    ans.append(key)
                    sentence.append(line)
                    break

        return sentence, ans

    @staticmethod
    def __fill_first(ques, key):

        words = {

            "what": "______",
            "which": "______",
            "who": "______",
            "where": "______",
            "where did": "______",
            "which were": "______",
            "when did": "In ______",
            "how many": "______",
        }

        fill = []
        ans = []
        for i in range(len(ques)):
            l = ques[i]
            ls = l.lower().split(" ")
            if " ".join(ls[:2]) in words.keys():
                ls[:2] = words[" ".join(ls[:2])]
                ls = " ".join(ls).split("?")[0] + '.'
                fill.append(ls)
                ans.append(key[i])
            elif ls[0] in words.keys():
                ls[0] = words[ls[0]]
                ls = " ".join(ls).split("?")[0] + '.'
                fill.append(ls)
                ans.append(key[i])
        return fill, ans

    @staticmethod
    def __fill_random(text):
        keys = Fill.__extract(text)
        sentence = Fill.__get_sentence(text)
        ques, ans = Fill.__generate(sentence, keys)
        return ques, ans

    @staticmethod
    def generate(text, min_ques, max_ques, fill_ques, fill_key):
        first_ques, first_ans = Fill.__fill_first(fill_ques, fill_key)
        random_ques, random_ans = Fill.__fill_random(text)

        ques = first_ques + random_ques
        ans = first_ans + random_ans
        final_ques = []
        final_ans = []
        ind = 0
        N = len(ques)
        for i in range(N):
            n = random.randint(0, len(ques)-1)
            if ans[n] not in final_ans:
                final_ques.append(ques[n])
                final_ans.append(ans[n])
                del ques[n]
                del ans[n]
                ind += 1

            if ind == max_ques:
                break

        return final_ques, final_ans
