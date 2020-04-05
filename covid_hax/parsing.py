def read_questions():
    with open("questions.txt") as f:
        lines = f.readlines()
    questions = {}
    for line in lines:
        splt = line.strip().split("(")
        answers = splt[1][:len(splt[1]) - 1]
        questions[splt[0]] = [answer.strip() for answer in answers.split(",")]
    return questions


def read_answers():
    with open("answers.txt") as f:
        lines = f.readlines()
    answers = {}
    conclusions = {}
    for line in lines:
        splt = line.strip().split(":")
        if len(splt) > 2:
            # final answer
            answers[splt[0]] = splt[2]
            conclusions[splt[0]] = splt[2]
        else:
            answers[splt[0]] = splt[1]
    return answers, conclusions
