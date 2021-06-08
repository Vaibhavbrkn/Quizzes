from setuptools import setup
setup(name="quizzes",
      version="0.2",
      description="package to generate MCQ questions with options and answer",
      author="Vaibhav Agrawal",
      packages=["quizzes"],
      install_requires=[
          'torch==1.8.1',
          'transformers==4.4.2',
          "numpy",
          "sentencepiece",
          "sense2vec",
          "keybert",
          "spacy",
      ],
      )
