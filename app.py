import dash
import dash_cytoscape as cyto
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import base64
import json

# Инициализация приложения
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY])
app.title = "Tree Editor"

# Загрузка дополнительных макетов для отображения дерева снизу вверх
cyto.load_extra_layouts()

# счетчик узлов
root_counter = 1
child_counter = 1

# создание пустого графа
elements_data = []

# выбор цветов для узлов
color_options = [
    {'label': 'Красный', 'value': 'red'},
    {'label': 'Зеленый', 'value': 'green'},
    {'label': 'Синий', 'value': 'blue'},
    {'label': 'Желтый', 'value': 'yellow'},
    {'label': 'Черный', 'value': 'black'},
    {'label': 'Серый', 'value': 'grey'},
    {'label': 'Фиолетовый', 'value': 'purple'},
    {'label': 'Оранжевый', 'value': 'orange'},
    {'label': 'Коричневый', 'value': 'brown'},
    {'label': 'Розовый', 'value': 'pink'},
    {'label': 'Бирюзовый', 'value': 'cyan'},
    {'label': 'Лаймовый', 'value': 'lime'},
    {'label': 'Серебристый', 'value': 'silver'},
    {'label': 'Золотой', 'value': 'gold'},
    {'label': 'Пурпурный', 'value': 'magenta'},
    {'label': 'Бордовый', 'value': 'maroon'},
    {'label': 'Темно-синий', 'value': 'navy'},
    {'label': 'Оливковый', 'value': 'olive'},
    {'label': 'Чирк', 'value': 'teal'},
    {'label': 'Аква', 'value': 'aqua'},
    {'label': 'Фуксия', 'value': 'fuchsia'},
    {'label': 'Серебристый', 'value': 'silver'}
]

# макет для управления графом
edit_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Управление графом"),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='layout-direction',
                        options=[
                            {'label': 'Сверху вниз', 'value': 'TB'},
                            {'label': 'Снизу вверх', 'value': 'BT'}
                        ],
                        value='TB',
                        placeholder='Выберите направление',
                        className='mb-2'
                    ),
                    dbc.Button('Добавить корень', id='add-root-btn', n_clicks=0, color='success',
                               className='mb-2', style={'width': '100%', 'background-color': '#50c878'}),
                    dcc.Input(id='root-label', type='text', placeholder='Название корня', className='mb-2',
                              style={'width': '100%'}),
                    dcc.Dropdown(
                        id='root-color',
                        options=color_options,
                        value='yellow',
                        placeholder='Выберите цвет корня',
                        className='mb-2'
                    ),
                    dcc.Checklist(
                        id='toggle-upload-images',
                        options=[{'label': 'Работа с изображениями', 'value': 'show'}],
                        value=[]
                    ),
                    html.Div(
                        id='upload-root-image-container',
                        children=[
                            dcc.Upload(
                                id='upload-root-image',
                                children=html.Div([
                                    'Перетащите или ',
                                    html.A('выберите файл')
                                ]),
                                style={
                                    'width': '100%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px 0'
                                },
                            ),
                            html.Div(id='upload-root-status', style={'textAlign': 'center'}),
                        ],
                        style={'display': 'none'}
                    ),
                    html.Br(),
                    dbc.Button('Добавить потомка', id='add-child-btn', n_clicks=0, color='primary', className='mb-2',
                               style={'width': '100%', 'background-color': '#1e90ff'}, disabled=True),
                    dcc.Input(id='child-label', type='text', placeholder='Название потомка', className='mb-2',
                              style={'width': '100%'}, disabled=True),
                    dcc.Input(id='edge-label', type='text', placeholder='Пометка', className='mb-2',
                              style={'width': '100%'}, disabled=True),
                    html.Br(),
                    dcc.Dropdown(
                        id='node-color',
                        options=color_options,
                        value='yellow',
                        placeholder='Выберите цвет узла',
                        className='mb-2'
                    ),
                    dcc.Dropdown(
                        id='edge-color',
                        options=color_options,
                        value='lightblue',
                        placeholder='Выберите цвет ребра',
                        className='mb-2'
                    ),
                    html.Div(
                        id='upload-image-container',
                        children=[
                            dcc.Upload(
                                id='upload-image',
                                children=html.Div([
                                    'Перетащите или ',
                                    html.A('выберите файл')
                                ]),
                                style={
                                    'width': '100%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px 0'
                                },
                            ),
                            html.Div(id='upload-status', style={'textAlign': 'center'}),
                        ],
                        style={'display': 'none'}
                    ),
                    html.Br(),
                    dbc.Button('Удалить узел', id='delete-node-btn', n_clicks=0, color='danger', className='mb-2',
                               style={'width': '100%', 'background-color': '#ff7f50'}, disabled=True),
                    html.Br(),
                    dbc.Button('Очистить граф', id='clear-tree-btn', n_clicks=0, color='warning', className='mb-2',
                               style={'width': '100%', 'background-color': '#f0ad4e'}),
                    html.Br(),
                    dcc.Input(id='filename', type='text', placeholder='Имя файла', className='mb-2',
                              style={'width': '100%'}),
                    dbc.Button('Сохранить граф', id='save-tree-btn', n_clicks=0, color='info', className='mb-2',
                               style={'width': '100%', 'background-color': '#ffeb3b'}),
                    dcc.Download(id='download-tree'),
                    html.Br(),
                    dcc.Upload(
                        id='upload-tree',
                        children=html.Div([
                            'Перетащите или ',
                            html.A('выберите JSON файл')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px 0'
                        },
                    ),
                    html.Div(id='upload-tree-status', style={'textAlign': 'center'})
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Граф"),
                dbc.CardBody([
                    cyto.Cytoscape(
                        id='cytoscape-tree',
                        layout={'name': 'dagre', 'rankDir': 'TB', 'align': 'UR'},
                        style={'width': '100%', 'height': '600px', 'border': '1px solid lightgrey',
                               'border-radius': '5px', 'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.2)'},
                        elements=elements_data,
                        stylesheet=[
                            {
                                'selector': 'node',
                                'style': {
                                    'label': 'data(label)',
                                    'background-color': 'data(color)',
                                    'color': 'black',
                                    'text-valign': 'top',
                                    'text-halign': 'center',
                                    'background-fit': 'cover',
                                    'background-image': 'data(url)'
                                }
                            },
                            {
                                'selector': 'edge',
                                'style': {
                                    'label': 'data(label)',
                                    'curve-style': 'bezier',
                                    'line-color': 'data(color)',
                                    'width': 2
                                }
                            },
                            {
                                'selector': 'node:selected',
                                'style': {
                                    'border-width': '2px',
                                    'border-color': 'blue'
                                }
                            }
                        ]
                    ),
                    html.Div([
                        dcc.Input(id='selected-node-label', type='text', placeholder='Изменить метку узла',
                                  className='mb-2', style={'width': '100%'}),
                        dcc.Input(id='selected-edge-label', type='text', placeholder='Изменить метку ребра',
                                  className='mb-2', style={'width': '100%'})
                    ], id='edit-labels-container', style={'display': 'none'}),
                ])
            ])
        ], width=9)
    ])
])

# Определение Layout
app.layout = html.Div([
    dcc.Store(id='root-counter', data=root_counter),
    dcc.Store(id='child-counter', data=child_counter),
    dcc.Store(id='root-added', data=False),
    edit_layout
])


@app.callback(
    [
        Output('cytoscape-tree', 'elements'),
        Output('add-child-btn', 'disabled'),
        Output('child-label', 'disabled'),
        Output('edge-label', 'disabled'),
        Output('delete-node-btn', 'disabled'),
        Output('upload-status', 'children'),
        Output('upload-tree-status', 'children'),
        Output('edit-labels-container', 'style'),
        Output('layout-direction', 'disabled'),
        Output('root-added', 'data')
    ],
    [
        Input('add-root-btn', 'n_clicks'),
        Input('add-child-btn', 'n_clicks'),
        Input('delete-node-btn', 'n_clicks'),
        Input('upload-root-image', 'contents'),
        Input('upload-image', 'contents'),
        Input('upload-tree', 'contents'),
        Input('selected-node-label', 'value'),
        Input('selected-edge-label', 'value'),
        Input('clear-tree-btn', 'n_clicks')
    ],
    [
        State('root-label', 'value'),
        State('root-color', 'value'),
        State('child-label', 'value'),
        State('edge-label', 'value'),
        State('node-color', 'value'),
        State('edge-color', 'value'),
        State('cytoscape-tree', 'elements'),
        State('cytoscape-tree', 'selectedNodeData'),
        State('cytoscape-tree', 'selectedEdgeData'),
        State('filename', 'value'),
        State('root-counter', 'data'),
        State('child-counter', 'data'),
        State('root-added', 'data')
    ]
)
def update_graph(add_root_clicks, add_child_clicks, delete_node_clicks, upload_root_image, upload_image, upload_tree,
                 selected_node_label, selected_edge_label, clear_tree_clicks,
                 root_label, root_color, child_label, edge_label, node_color, edge_color,
                 elements, selected_nodes, selected_edges, filename, root_counter, child_counter, root_added):
    ctx = dash.callback_context
    upload_status = ""
    upload_tree_status = ""
    edit_labels_style = {'display': 'none'}
    if not elements:
        elements = []
    if not selected_nodes:
        selected_nodes = []
    if not selected_edges:
        selected_edges = []
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'add-root-btn' and not root_added:
            new_node = {
                'data': {'id': f'r{root_counter}', 'label': root_label or '', 'color': root_color},
                'position': {'x': 0, 'y': 0}
            }
            if upload_root_image:
                content_type, content_string = upload_root_image.split(',')
                data_url = f'data:{content_type};base64,{content_string}'
                new_node['data']['url'] = data_url

            elements.append(new_node)
            root_counter += 1
            root_added = True
        elif button_id == 'add-child-btn' and selected_nodes:
            parent_id = selected_nodes[0]['id']
            new_node = {
                'data': {'id': f'c{child_counter}', 'label': child_label or '', 'color': node_color},
                'position': {'x': 0, 'y': 0}
            }
            if upload_image:
                content_type, content_string = upload_image.split(',')
                data_url = f'data:{content_type};base64,{content_string}'
                new_node['data']['url'] = data_url

            new_edge = {
                'data': {'source': parent_id, 'target': f'c{child_counter}', 'label': edge_label or '',
                         'color': edge_color}
            }
            elements.append(new_node)
            elements.append(new_edge)
            child_counter += 1

        elif button_id == 'delete-node-btn' and selected_nodes:
            node_id = selected_nodes[0]['id']
            elements = [el for el in elements if not (
                    el['data'].get('id') == node_id or el['data'].get('source') == node_id or el['data'].get(
                'target') == node_id)]

        elif button_id == 'upload-image' and upload_image:
            content_type, content_string = upload_image.split(',')
            decoded = base64.b64decode(content_string)
            data_url = f'data:{content_type};base64,{content_string}'

            if selected_nodes:
                node_id = selected_nodes[0]['id']
                for el in elements:
                    if el['data'].get('id') == node_id:
                        el['data']['url'] = data_url
                        upload_status = "Изображение успешно загружено"

        elif button_id == 'upload-tree' and upload_tree:
            content_type, content_string = upload_tree.split(',')
            decoded = base64.b64decode(content_string)
            tree_json = json.loads(decoded.decode('utf-8'))
            elements = tree_json['elements']
            upload_tree_status = "Дерево успешно загружено"

        elif button_id == 'selected-node-label' and selected_nodes:
            node_id = selected_nodes[0]['id']
            for el in elements:
                if el['data'].get('id') == node_id:
                    el['data']['label'] = selected_node_label or ''

        elif button_id == 'selected-edge-label' and selected_edges:
            edge_id = selected_edges[0]['id']
            for el in elements:
                if el['data'].get('id') == edge_id:
                    el['data']['label'] = selected_edge_label or ''

        elif button_id == 'clear-tree-btn':
            elements = []
            root_counter = 1
            child_counter = 1
            root_added = False

    if selected_nodes or selected_edges:
        edit_labels_style = {'display': 'block'}

    return elements, not elements, not elements, not elements, not elements, upload_status, upload_tree_status, \
        edit_labels_style, root_added, root_added


@app.callback(
    [Output('root-counter', 'data'),
     Output('child-counter', 'data')],
    [Input('add-root-btn', 'n_clicks'),
     Input('add-child-btn', 'n_clicks'),
     Input('clear-tree-btn', 'n_clicks')],
    [State('root-counter', 'data'),
     State('child-counter', 'data')]
)
def update_counters(add_root_clicks, add_child_clicks, clear_tree_clicks, root_counter, child_counter):
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'add-root-btn':
            root_counter += 1
        elif button_id == 'add-child-btn':
            child_counter += 1
        elif button_id == 'clear-tree-btn':
            root_counter = 1
            child_counter = 1
    return root_counter, child_counter


@app.callback(
    Output('download-tree', 'data'),
    Input('save-tree-btn', 'n_clicks'),
    State('cytoscape-tree', 'elements'),
    State('filename', 'value')
)
def save_tree(n_clicks, elements, filename):
    if n_clicks:
        filename = filename or 'graph'
        return dict(content=json.dumps({'elements': elements}), filename=f"{filename}.json")


@app.callback(
    Output('cytoscape-tree', 'layout'),
    [Input('layout-direction', 'value')],
    [State('root-added', 'data')]
)
def update_layout(direction, root_added):
    if root_added:
        raise dash.exceptions.PreventUpdate
    return {'name': 'dagre', 'rankDir': direction, 'align': 'UR'}


@app.callback(
    [Output('upload-root-image-container', 'style'),
     Output('upload-image-container', 'style')],
    Input('toggle-upload-images', 'value')
)
def toggle_upload_images(value):
    if value:
        return {'display': 'block'}, {'display': 'block'}
    return {'display': 'none'}, {'display': 'none'}


if __name__ == '__main__':
    app.run_server(debug=True)
