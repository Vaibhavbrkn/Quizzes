# quizzes: Generate question-answers

## ✨ Features

- **Generate MCQ from passage with options**

## 🚀 Quickstart

> First download the [sense2vec weight](https://github.com/explosion/sense2vec/releases/download/v1.0.0/s2v_reddit_2015_md.tar.gz). Unzip it and place it into a path.

```bash
pip install quizzes
```

```python
from quizzes import Question

Q  = Question("path of sense2vec weight")
ques, ans = Q.generate("your passage" , min_question = 5, max_question = 8)
# ques: List of question,
#  ans: List of choice of question with first option as answer
```
