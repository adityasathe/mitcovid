import numpy as np


class AnswerNode:

    def __init__(self, answer):
        self.answer = answer
        self.next_questions = {}
        self.conclusions = {}  # Dict[Conclusion, float]

    def pick_next_question(self, skips=None):
        questions = []
        probs = []
        for q in self.next_questions:
            if skips is None or q not in skips:
                questions.append(q)
                probs.append(self.next_questions[q])
        for q in skips:
            assert q not in questions
        if len(questions) < 1:
            return None
        return np.random.choice(questions, 1, probs)[0]

    def assign_weights(self, weights):
        for question in self.next_questions:
            if question.question in weights:
                self.next_questions[question] = weights[question.question]


class QueryNode:

    def __init__(self, question):
        self.question = question  # str
        self.answers = {}  # Dict[str, AnswerNode]

    def __eq__(self, other):
        return self.question == other.question

    def __hash__(self):
        return hash(self.question)

    def relevance(self, conclusion=None):
        relevance = 0.0
        for answer in self.answers.values():
            if conclusion is None:
                for conc in answer.conclusions:
                    relevance += answer.conclusions[conc]
            elif conclusion in answer.conclusions:
                relevance += answer.conclusions[conclusion]
        return relevance


class Conclusion:

    def __init__(self, conclusion):
        self.conclusion = conclusion

    def __eq__(self, other):
        return self.conclusion == other.conclusion

    def __hash__(self):
        return hash(self.conclusion)


