from typing import Tuple
from spiral import ronin
from igraph import Graph, EdgeSeq, plot
import plotly.graph_objects as go

fig = go.Figure()
import csv
import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import json
import pandas as pd
import plotly.express as px


class TrieNode(object):
    """
    Our trie node implementation. Very basic. but does the job
    """

    def __init__(self, word: str):
        self.word = word
        self.children = []
        # Is it the last character of the word.`
        self.word_finished = False
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
    node.word_finished = True
    return node


def find_prefix(root, word: str) -> Tuple[bool, int]:
    """
    Check and return
      1. If the prefix exsists in any of the words we added so far
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


def trienode2graph(root, graph, labels):
    for child in root.children:
        if child.word not in labels.keys():
            graph.add_vertices(1)
            labels[child.word] = list(labels.values())[-1] + 1
        graph.add_edges([(labels[root.word], labels[child.word])])
        trienode2graph(child, graph, labels)


def build_graph(root):
    graph = Graph()
    labels = {'*': 0}  # dictionary:
    graph.add_vertices(1)
    trienode2graph(root, graph, labels)
    return graph, labels


def plot_graph(graph, text):
    nr_vertices = len(labels)
    lay = graph.layout('rt')

    position = {k: lay[k] for k in range(nr_vertices)}
    Y = [lay[k][1] for k in range(nr_vertices)]
    M = max(Y)

    E = [e.tuple for e in graph.es]  # list of edges

    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [2 * M - position[k][1] for k in range(L)]
    Xe = []
    Ye = []
    for edge in E:
        Xe += [position[edge[0]][0], position[edge[1]][0], None]
        Ye += [2 * M - position[edge[0]][1], 2 * M - position[edge[1]][1], None]

    fig.add_trace(go.Scatter(x=Xe,
                             y=Ye,
                             mode='lines',
                             line=dict(color='rgb(210,210,210)', width=1),
                             hoverinfo='none'
                             ))
    fig.add_trace(go.Scatter(x=Xn,
                             y=Yn,
                             mode='markers',
                             name='Words',
                             marker=dict(symbol='circle-dot',
                                         size=25,
                                         color='#6175c1',  # '#DB4551',
                                         line=dict(color='rgb(50,50,50)', width=1)
                                         ),
                             text=text,
                             hoverinfo='text',
                             opacity=0.8
                             ))

    def make_annotations(pos, text, font_size=8, font_color='rgb(250,250,250)'):
        L = len(pos)
        if len(text) != L:
            raise ValueError('The lists pos and text must have the same len')
        annotations = []
        for k in range(L):
            annotations.append(
                dict(
                    text=text[k],  # or replace labels with a different list for the text within the circle
                    x=pos[k][0], y=2 * M - position[k][1],
                    xref='x1', yref='y1',
                    font=dict(color=font_color, size=font_size),
                    showarrow=False)
            )
        return annotations

    axis = dict(showline=False,  # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                )

    fig.update_layout(title='NameSplitter Binary Tree',
                      annotations=make_annotations(position, text),
                      font_size=16,
                      showlegend=False,
                      xaxis=axis,
                      yaxis=axis,
                      margin_autoexpand=True,
                      hovermode='closest',
                      clickmode='event+select',
                      plot_bgcolor='rgb(248,248,248)',
                      width=1920,
                      height=1080
                      # dragmode='select'
                      )

    # fig.update_traces(
    #     line=dict(dash="dot", width=4),
    #     selector=dict(type="scatter", mode="lines"))

    # scatter = fig.data[0]
    #
    # def update_point(trace, points, selector):
    #     c = list(scatter.marker.color)
    #     s = list(scatter.marker.size)
    #     for i in points.point_inds:
    #         c[i] = '#bae2be'
    #         s[i] = 20
    #         with fig.batch_update():
    #             scatter.marker.color = c
    #             scatter.marker.size = s
    #
    # scatter.on_click(update_point)
    # fig.update_traces(marker=dict(color="RoyalBlue"))

    fig.update_yaxes(automargin=True)
    fig.update_xaxes(automargin=True)
    fig.show()


app = dash.Dash()


@app.callback(
    Output('click-data', 'children'),
    Input('basic-interactions', 'clickData'))
# def update_points(clickData):
#     return json.dumps(clickData, indent=2)

def update_points(clickData):
    fig.up
    return fig

app.layout = html.Div([
    dcc.Graph(figure=fig,
              id='basic-interactions')
])

filename = open('training_data.csv', 'r')

file = csv.DictReader(filename)

words1 = []

# pandas data frame
# dfb = pd.read_csv("training_data.csv")
# df = px.data.tips()
# fig = px.pie(dfb, values='IDENTIFIER', names='IDENTIFIER')
# fig.show()


for col in file:
    words1.append(col['IDENTIFIER'])

root = TrieNode('*')
for words in words1:
    node = root
    for word in ronin.split(words):
        node = add(node, word)

graph, labels = build_graph(root)
plot_graph(graph, list(labels.keys()))
app.run_server(debug=True, use_reloader=True)
