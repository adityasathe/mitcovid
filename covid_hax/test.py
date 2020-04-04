from graph import *
from building import *
from respondent import *
from parsing import *

import numpy as np

initial_questions = read_questions()
initial_answers, initial_conclusions = read_answers()

# Quick hack
remove_list = []
for q in initial_questions:
    for a in initial_questions[q]:
        if a not in initial_answers:
            remove_list.append(a)
    for a in remove_list:
        initial_questions[q].remove(a)
    remove_list.clear()

def build_graph(answers, questions, conclusions):
    nodes = [build_node(q, answers) for q in questions]
    connect_nodes(nodes)
    add_conclusions(nodes, conclusions)

    return QueryGraph(nodes)

def seed_weights(answers, questions, conclusions):
    pass

for a in answers:
    for q in answers[a]:
        if q in questions:


# questions = ["a?", "b?", "c?", "d?", "e?", "f?"]
#
#
# answers = ["yes", "no"]
#
# conclusions = ["1", "2", "3", "4"]


bias_signal = BiasHelper(initial_conclusions[0], {"a?": "yes", "b?": "yes", "c?": "yes"}, 0.5)


def do_graph_session(graph):
    conc = np.random.choice(conclusions, 1)[0]
    qs = QuerySession(graph, conc)
    if conc == "1":
        print("BIAS IN PLACE")
        respondent = Respondent(bias_signal.get_biases())
    else:
        respondent = Respondent({})
    for i in range(3):
        print(qs.current_query.question)
        answer = respondent.answer_question(qs.current_query)
        print(answer)
        qs.receive_answer_for_next_question(answer)
        if respondent.biases:
            print("biased")
            if qs.current_query.question == "d?":
                print("error")
                yes_answers = qs.asked_questions[len(qs.asked_questions) - 1].answers["yes"]
                print(yes_answers)
                for q in yes_answers.next_questions:
                    print(q.question)
                    print(yes_answers.next_questions[q])
    print("--------- END OF SESSION ---------")
    return qs.get_session_result()


results = SessionResults(nodes, conclusions)

for i in range(1000):
    results.add_result(do_graph_session(qg))


correlation_results = results.result_matrices[conclusions[0]].get_correlation()


# nodes = [build_node(q, answers) for q in questions]
# connect_nodes(nodes)
# add_conclusions(nodes, conclusions)

for node in nodes:
    add_weights(node, correlation_results[node.question])


add_conclusions(nodes, conclusions)
weighted_graph = QueryGraph(nodes)

for i in range(1000):
    results.add_result(do_graph_session(weighted_graph))
