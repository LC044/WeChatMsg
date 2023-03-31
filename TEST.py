import json

from pyecharts import options as opts
from pyecharts.charts import Graph

with open(r'data/npmdepgraph.min10.json', 'r') as f:
    data = json.load(f)

nodes = [
    {
        'x': node['x'],
        'y': node['y'],
        'name': node['label'],
        'symbolSize': node['size'],
        'itemStyle': {'color': node['color']}
    }
    for node in data['nodes']
]

edges = [
    {
        'source': edge['sourceID'],
        'target': edge['targetID']
    }
    for edge in data['edges']
]

G = Graph(init_opts=opts.InitOpts(width='900', height='900'))
G.add(
    series_name='',
    nodes=nodes,
    links=edges,
    layout='none',
    is_roam=True,
    is_focusnode=True,
    label_opts=opts.LabelOpts(is_show=True),
    linestyle_opts=opts.LineStyleOpts(width=0.5, curve=0.3, opacity=0.7)
)
G.set_global_opts(title_opts=opts.TitleOpts(title='NPM Dependencies'))
G.render('npm_dependencies.html')
