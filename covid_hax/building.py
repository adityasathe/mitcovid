from query import *


def add_weights(query_node, weights):
    for answer in query_node.answers:
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
    for node in nodes:
        for answer in node.answers.values():
            for conclusion in conclusions:
                answer.conclusions[conclusion] = 0.0  # No weight initially
