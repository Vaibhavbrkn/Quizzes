# quizzes: Generate question-answers

## ✨ Features

- **Generate MCQ from passage with options**

## 🚀 Quickstart

> First download the [sense2vec weight](https://drive.google.com/drive/folders/14TCl8EUra0a7Xl_29hr7sgKOWrMGpyV1?usp=sharing). Unzip it and place it into a path.

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
