import igraph
from igraph import Graph, EdgeSeq
import plotly.graph_objects as go
from spiral import ronin

g = Graph()
g.add_vertices(14)
g.add_edges([(0,1), (0,2), (1,2), (2,2), (2,3)])

for words in ['mStartCData', 'mStartDData', 'nonnegativedecimaltype', 'nonnegativePositiveNumbers', 'getUtf8Octets',
              'savefileas', 'nbrOfbugs']:
    g.vs
    g.vs["name"] = ronin.split(words)
print(g)