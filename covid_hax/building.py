from query import *


def add_correlations(query_node, correlations):
    for answer in query_node.answers.values():
        if answer.answer not in correlations:
            continue
        scores = {q: 0 for q in answer.next_questions}
        for q in answer.next_questions:
            if q.is_conclusion():
                return
            for a in q.answers.values():
                if a.answer in correlations[answer.answer]:
                    scores[q] += correlations[answer.answer][a.answer]
        answer.next_questions = scores


def add_weights(query_node, weights):
    for answer in query_node.answers:
        if answer not in weights:
            continue
        next_question_weights = weights[answer]
        query_node.answers[answer].assign_weights(next_question_weights)


def build_node(question, answers):
    qn = QueryNode(question)
    for answer in answers:
        an = AnswerNode(answer)
        qn.answers[answer] = an
    return qn


def attach_nodes_to_node(query_node, query_nodes):
    for answer in query_node.answers.values():
        for node in query_nodes:
            answer.next_questions[node] = 1.0 / len(query_nodes)  # Equal probability initially


def connect_nodes(nodes):
    num_nodes = len(nodes)
    for i in range(num_nodes):
        node = nodes.pop(0)
        attach_nodes_to_node(node, nodes)
        nodes.append(node)


def add_conclusions(nodes, conclusions):
    conc = {c: conclusions[c] for c in conclusions if '*' not in c}
    for c in conclusions:
        if '*' in c:
            conc[c[1:]] = conclusions[c]
    for node in nodes:
        for answer in node.answers.values():
            if answer.answer not in conc:
                continue
            answer.next_questions[Conclusion(conc[answer.answer])] = 0.0  # No weight initially
