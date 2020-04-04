import numpy as np
import random


class BiasHelper:

    def __init__(self, conclusion, question_answers, probability_of_bias):
        self.conclusion = conclusion
        self.question_answers = question_answers
        self.prob = probability_of_bias

    def get_biases(self):
        if random.random() <= self.prob:
            return self.question_answers
        else:
            return {}


class Respondent:

    def __init__(self, biases):
        self.biases = biases  # -> Dict[str, str]

    def answer_question(self, query_node):
        if query_node.question in self.biases:
            return self.biases[query_node.question]  # Get the biased answer here
        else:
            choices = [answer for answer in query_node.answers.keys()]
            return np.random.choice(choices)
