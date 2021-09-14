from typing import Tuple
import pydot
from spiral import ronin


class TrieNode(object):
    """
    Our trie node implementation. Very basic. but does the job
    """

    def __init__(self, word: str):
        self.word = word
        self.children = []
        # Is it the last character of the word.`
        # self.word_finished = False
        # How many times this character appeared in the addition process
        self.counter = 1


def add(root, word: str):
    """
    Adding a word in the trie structure
    """
    # Search for the character in the children of the present `node`
    for child in root.children:
        if child.word == word:
            # We found it, increase the counter by 1 to keep track that another
            # word has it as well
            child.counter += 1
            # And point the node to the child that contains this char
            return child
    # We did not find it so add a new child
    node = TrieNode(word)
    root.children.append(node)
    # Everything finished. Mark it as the end of a word.
    # node.word_finished = True
    return node
    # returns node

def find_prefix(root, word: str) -> Tuple[bool, int]:
    """
    Check and return
      1. If the prefix exists in any of the words we added so far
      2. If yes then how may words actually have the prefix
    """

    node = root
    # If the root node has no children, then return False.
    # Because it means we are trying to search in an empty trie
    if not root.children:
        return False, 0

    '''for word in prefix:'''
    print(word)
    word_not_found = True
    # Search through all the children of the present `node`
    for child in node.children:
        if child.word == word:
            # We found the char existing in the child.
            word_not_found = False
            # Assign node as the child containing the char and break
            node = child
            break
    # Return False anyway when we did not find a char.
    if word_not_found:
        return False, 0
    # Well, we are here means we have found the prefix. Return true to indicate that
    # And also the counter of the last node. This indicates how many words have this
    # prefix
    return True, node.counter


def draw(graph, parent_name, child_name):
    edge = pydot.Edge(parent_name, child_name)
    graph.add_edge(edge)

# recursive function to convert trienode to pydot graph
def trienode2graph(root, graph):
    for child in root.children:
        # set edge from root to child
        draw(graph, root.word, child.word)
        # recursive call
        trienode2graph(child, graph)


if __name__ == "__main__":
    root = TrieNode('*')
    for words in ['mStartCData', 'mStartDData', 'nonnegativedecimaltype','nonnegativePositiveNumbers', 'getUtf8Octets',
              'savefileas', 'nbrOfbugs']:
        node = root
        for word in ronin.split(words):
            node = add(node, word)

    graph = pydot.Dot(graph_type='graph')
    trienode2graph(root, graph)
    graph.write_png('result.png')

