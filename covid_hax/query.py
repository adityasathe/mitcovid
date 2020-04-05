import numpy as np

SEED = 0
np.random.seed(SEED)


class AnswerNode:

    def __init__(self, answer):
        self.answer = answer
        self.next_questions = {}

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
        # We now have to normalize probabilities to 1 again
        if skips:
            tot = 0.0
            for p in probs:
                tot += p
            for i, p in enumerate(probs):
                probs[i] = (p / tot)

        choice = np.random.choice(questions, 1, p=probs)[0]
        return choice

    def assign_weights(self, weights):
        for question in self.next_questions:
            if question.is_conclusion():
                continue
            if question.value in weights:
                if weights[question.value] != weights[question.value]:
                    # nan
                    continue
                self.next_questions[question] = weights[question.value]

    def inspect(self):
        print("ANSWER: ")
        print(self.answer)
        print("------------ NEXT QUESTIONS -----------")
        for q in self.next_questions:
            print(q.value + " (" + str(self.next_questions[q]) + ")")
        print("----------")


class QueryNode:

    def __init__(self, question):
        self.value = question  # str
        self.answers = {}  # Dict[str, AnswerNode]

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    @staticmethod
    def is_conclusion():
        return False

    def relevance(self, conclusion=None):
        relevance = 0.0
        for answer in self.answers.values():
            if conclusion is None:
                for conc in answer.conclusions:
                    relevance += answer.conclusions[conc]
            elif conclusion in answer.conclusions:
                relevance += answer.conclusions[conclusion]
        return relevance

    def inspect(self):
        for answer in self.answers.values():
            answer.inspect()


class Conclusion:

    def __init__(self, conclusion):
        self.value = conclusion

    @staticmethod
    def is_conclusion():
        return True

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)


