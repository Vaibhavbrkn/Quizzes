# quizzes: Generate question-answers

## ✨ Features

- **Generate MCQ from passage with options**

## 🚀 Quickstart

> First download the [sense2vec weight](https://drive.google.com/drive/folders/14TCl8EUra0a7Xl_29hr7sgKOWrMGpyV1?usp=sharing). Unzip it and place it into a path.

```bash
pip install git+https://github.com/Vaibhavbrkn/Quizzes.git
pip install git+https://github.com/Vaibhavbrkn/pke.git
```

```python
from quizzes import Question

Q  = Question("path of sense2vec weight")
output = Q.generate("your passage" , min_question = 5, max_question = 8, min_fill_ques = 2, max_fill_ques=4)
"""
Output:
  {
    "mcq":[
            {
              "question":".....",
              "answer":"...",
              "choice":[]
            }
            ...
          ],
    "fill":[
            {
              "question"".....",
                "answer":"..."
            }
            ...
          ]
  }

"""

```
