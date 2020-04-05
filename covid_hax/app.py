from flask import Flask, request, jsonify
from graph import *
from building import *
from respondent import *
from parsing import *

import numpy as np

app = Flask(__name__)

SEED = 0


SOFT_WEIGHT = 0.95
NUM_QUESTIONS_TO_ASK = 4


def get_next_question_initial_weights(answer, best_next_question, hard_bias):
    best_next_question_weight = SOFT_WEIGHT
    if hard_bias:
        best_next_question_weight = 1.0

    other_questions_weight = 1.0
    if len(answer.next_questions) > 1:
        other_questions_weight = (1.0 - best_next_question_weight) / (len(answer.next_questions) - 1)

    weights = {}
    for question in answer.next_questions:
        if question.is_conclusion():
            continue
        if question.value == best_next_question:
            weights[question.value] = best_next_question_weight
        else:
            weights[question.value] = other_questions_weight
    return weights


def set_conclusion(answer, conclusion, hard_bias):
    if hard_bias:
        for next_node in answer.next_questions:
            if next_node.is_conclusion() and next_node.value == conclusion:
                answer.next_questions[next_node] = 1.0
            else:
                answer.next_questions[next_node] = 0.0
    else:
        other_weight = 1.0
        if len(answer.next_questions) > 1:
            other_weight = (1.0 - SOFT_WEIGHT) / (len(answer.next_questions) - 1)
        for next_node in answer.next_questions:
            if next_node.is_conclusion() and next_node.value == conclusion:
                answer.next_questions[next_node] = SOFT_WEIGHT
            else:
                answer.next_questions[next_node] = other_weight


def add_initial_biases(nodes, answers, conclusions, hard_bias=True):
    for node in nodes:
        weights = {}
        for node_answer in node.answers.values():
            hardwired = '*' + node_answer.answer
            if node_answer.answer in conclusions or hardwired in conclusions:
                if node_answer.answer in conclusions:
                    conc = conclusions[node_answer.answer]
                else:
                    conc = conclusions[hardwired]
                set_conclusion(node_answer, conc, hard_bias or hardwired in conclusions)
            elif node_answer.answer in answers or hardwired in answers:
                if node_answer.answer in answers:
                    next_q = answers[node_answer.answer]
                else:
                    next_q = answers[hardwired]
                weights[node_answer.answer] = get_next_question_initial_weights(node_answer, next_q, hard_bias or hardwired in conclusions)
        add_weights(node, weights)


def build_initial_graph(answers, questions, conclusions):
    nodes = [build_node(q, questions[q]) for q in questions]
    connect_nodes(nodes)
    add_conclusions(nodes, conclusions)
    add_initial_biases(nodes, answers, conclusions, False)

    return nodes, QueryGraph(nodes)


def rebuild_graph(questions, answers, conclusions, correlations):
    nodes = [build_node(q, questions[q]) for q in questions]
    connect_nodes(nodes)
    add_conclusions(nodes, conclusions)
    add_initial_biases(nodes, answers, conclusions, False)

    for node in nodes:
        add_correlations(node, correlations)

    return QueryGraph(nodes)


def do_graph_session(graph):
    conc = np.random.choice(test_conclusions, 1)[0]
    qs = QuerySession(graph, conc)
    respondent = Respondent(bias_signal.get_biases())
    for i in range(NUM_QUESTIONS_TO_ASK):
        answer = respondent.answer_question(qs.current_query)
        qs.receive_answer_for_next_question(answer)
        if qs.current_query.is_conclusion():
            break
    return qs.get_session_result()


@app.route("/graph/rebuild")
def rebuild():
    global results, graph

    results.rank_line_of_questions(5)

    print("--------- REBUILDING ----------")

    correlation_results = results.result_matrix.get_correlation()
    graph = rebuild_graph(initial_questions, initial_answers, initial_conclusions, correlation_results)
    results = SessionResults(nodes, test_conclusions)
    return "OK"


@app.route("/session/do")
def session():
    results.add_result(do_graph_session(graph))
    return "OK"


@app.route("/session/user")
def user_sesh():
    global user_sesh, graph, started
    if not started:
        user_sesh = QuerySession(graph)
        started = True
    else:
        answer = request.args['answer']
        user_sesh.receive_answer_for_next_question(answer)
    next_question = user_sesh.current_query
    resp = {'question': next_question.value, 'answers': {str(i): answer for i, answer in enumerate(next_question.answers)}}
    return jsonify(resp)


if __name__ == "__main__":
    np.random.seed(SEED)

    initial_questions = read_questions()
    initial_answers, initial_conclusions = read_answers()

    # Quick hack
    remove_list = []
    for q in initial_questions:
        for a in initial_questions[q]:
            hardwired = '*' + a
            if a not in initial_answers and hardwired not in initial_answers:
                remove_list.append(a)
        for a in remove_list:
            initial_questions[q].remove(a)
        remove_list.clear()

    nodes, graph = build_initial_graph(initial_answers, initial_questions, initial_conclusions)

    # Example: it seems that people who are from New Jersey are getting sick and are indifferent. Let's introduce this
    # as a hidden signal and see if we can find something.
    related_questions = ["What concerns you about coronavirus today?",
                         "What would you like to know about social distancing?", "Where are you from?"]
    related_answers = ["I think I have been exposed to COVID-19", "Why should I care?", "New Jersey"]
    bias_signal = BiasHelper("", {related_questions[i]: related_answers[i] for i in range(len(related_questions))}, 0.5)

    test_conclusions = [ic for ic in initial_conclusions.values()]

    results = SessionResults(nodes, test_conclusions)
    started = False
    app.run(debug=True, host='0.0.0.0')
