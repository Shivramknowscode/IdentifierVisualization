import base64
import datetime
import io

from typing import Tuple
from spiral import ronin
from igraph import Graph, EdgeSeq, plot
import plotly.graph_objects as go
import csv
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, callback_context
from dash import html
import json
import pandas as pd
import plotly.express as px
from dash import dash_table

fig = go.Figure()
# external_scripts =[]

# [
#     'https://www.google-analytics.com/analytics.js',
#     {'src': '/Users/shivram/PycharmProjects/NameSplitter/spiral/tests/custom-script.js'},
#     {
#         'src': '/Users/shivram/PycharmProjects/NameSplitter/spiral/tests/custom-script.js',
#         'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
#         'crossorigin': 'anonymous'
#     }
# ]


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
    labels = {root.word: 0}  # dictionary:
    graph.add_vertices(1)
    trienode2graph(root, graph, labels)
    return graph, labels


def plot_graph(graph, text):
    nr_vertices = len(text)
    app.logger.info(text)
    # nr_vertices = len(labels)
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
    # fig.data = []
    # fig.layout = {}
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
                                         size=50,
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


app = dash.Dash(__name__)

# ,
# external_scripts=external_scripts)


# @app.callback(
#     Output('click-data', 'children'),
#     Input('basic-interactions', 'clickData'))
# def update_points(clickData):
#     return json.dumps(clickData, indent=2)

first_words = []
identifiers = []


def set_csv(userUploadedFile):
    filename = open(userUploadedFile, 'r')
    file = csv.DictReader(filename)
    # app.logger.info(json.dumps(file))
    for col in file:
        identifiers.append(col['IDENTIFIER'])

    split_identifiers = [x.split()[0] for x in identifiers]

    for i in split_identifiers:
        if i not in first_words:
            first_words.append(i)

    # app.logger.info(first_words)
    # app.logger.info(identifiers)


def dropbox_layout():
    return html.Div([
        dcc.Interval(
            id='interval-component',
            interval=10 * 1000,  # in milliseconds
            n_intervals=0
        ),
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
            html.Div(id='output-data-upload')
        ])
    ])


def input_menu_layout():
    return html.Div([
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        ),
        html.Div([
            html.Div(dcc.Input(id='input-box', type='text')),
            html.Button('Submit', id='button'),
            html.Div(id='output-container-button',
                     children='Enter a value and press submit')
        ]),

        html.Div([
            dcc.Dropdown(
                id='select_identifier',
                options=[
                    {'label': i, 'value': i} for i in first_words

                ],
                value='Identifier-Names'
            ), html.Div(id='dd-output-container')

        ])
    ])


def graph_layout():
    return html.Div([
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        ),
        html.Div(
            [
                dcc.Graph(figure=fig,
                          id='basic-interactions')

            ]),
        html.Div([
            html.Button('Back', id='btn-nclicks-1', n_clicks=0),
            html.Div(id='container-button-timestamp')
        ])
    ])


app.layout = dropbox_layout


# app.layout = html.Div(
#
#     [
#
#         html.Div([
#             dcc.Upload(
#                 id='upload-data',
#                 children=html.Div([
#                     'Drag and Drop or ',
#                     html.A('Select Files')
#                 ]),
#                 style={
#                     'width': '100%',
#                     'height': '60px',
#                     'lineHeight': '60px',
#                     'borderWidth': '1px',
#                     'borderStyle': 'dashed',
#                     'borderRadius': '5px',
#                     'textAlign': 'center',
#                     'margin': '10px'
#                 },
#                 # Allow multiple files to be uploaded
#                 multiple=True
#             ),
#             html.Div(id='output-data-upload'),
#         ]),
#
#         html.Div([
#             html.Div(dcc.Input(id='input-box', type='text')),
#             html.Button('Submit', id='button'),
#             html.Div(id='output-container-button',
#                      children='Enter a value and press submit')
#         ]),
#
#         html.Div([
#             dcc.Dropdown(
#                 id='select_identifier',
#                 options=[
#                     {'label': i, 'value': i} for i in first_words
#
#                 ],
#                 value='Identifier Names'
#             ), html.Div(id='dd-output-container')
#         ]),
#
#         html.Div(
#             [
#                 dcc.Graph(figure=fig,
#                           id='basic-interactions')
#
#             ])
#     ])


def find_node(root, queryWord):
    if root.word == queryWord:
        return root
    for child in root.children:
        node = find_node(child, queryWord)
        if node is not None:
            return node
    return None


def createGraphFromWord(queryWord):
    node = find_node(main_root, queryWord)
    app.logger.info(main_root)
    app.logger.info(queryWord)
    if node is None:
        return
    graph, labels = build_graph(node)
    plot_graph(graph, list(labels.keys()))


@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')])
# Input('interval-component', 'n_intervals'))
def update_output(n_clicks, value):
    createGraphFromWord(value)
    app.layout = graph_layout()
    return 'The input value was "{}" and the button has been clicked {} times'.format(
        value,
        n_clicks
    )


@app.callback(
    Output('dd-output-container', 'children'),
    Input('select_identifier', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_output(value, n):
    createGraphFromWord(value)
    app.layout = graph_layout()
    return 'You have selected "{}"'.format(value)


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            set_csv(filename)
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))

        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            set_csv(filename)
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              Input('interval-component', 'n_intervals'))
def update_output(list_of_contents, list_of_names, list_of_dates, n):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        app.layout = input_menu_layout()
        return children


@app.callback(
    Output('container-button-timestamp', 'children'),
    Input('btn-nclicks-1', 'n_clicks'),
    Input('interval-component', 'n_intervals')
)
def displayClick(btn1, n):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn-nclicks-1' in changed_id:
        app.layout = input_menu_layout()
        msg = 'Going back....'
    else:
        msg = 'Not going back...'
    return html.Div(msg)


main_root = TrieNode('*')
for splitIdentifier in identifiers:
    node = main_root
    for word in ronin.split(splitIdentifier):
        node = add(node, word)

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)
