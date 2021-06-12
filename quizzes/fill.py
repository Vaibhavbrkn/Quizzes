


class Fill:
    
    @staticmethod
    def __fill_first(ques, key):
        
        words = {
    "what":"______",
    "which": "______",
    "who": "______",    
    "where": "______",
    "where did": "______",
    "which were":"______",
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
                ls = " ".join(ls)
                fill.append(ls)
                ans.append(key[i])
            elif ls[0] in words.keys():
                ls[0] = words[ls[0]]
                ls = " ".join(ls)
                fill.append(ls)
                ans.append(key[i])
        return fill , ans
    
    @staticmethod
    def __fill_random():
        pass
    
    @staticmethod
    def generate(text, min_ques, max_ques, fill_ques, fill_key):
        first_ques, first_ans = Fill.__fill_first(fill_ques, fill_key)
        return first_ques, first_ans