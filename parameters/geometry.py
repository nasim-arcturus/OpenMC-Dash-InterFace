import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Output, State, Input
from dash.exceptions import PreventUpdate

from app import app

layout = html.Div([
    html.H2('Geometry Configuration',
            style={
                'position': 'relative',
                'top': '0px',
                'left': '10px',
                'font-family': 'Dosis',
                'display': 'inline',
                'font-size': '4.0rem',
                'color': '#4D637F'
            }),
    html.Div(style=dict(height=20)),

    html.P("""
        Second, we need to create our geometries. As an overview, since this interface currently
        only supports geometry settings for a standard PWR/BWR i.e. radial planes for fuel 
        rods and rectangular lattice configurations, we will begin by defining pin cells in which our
        fuel & absorbers rods, water holes, etc will reside. Once pin cell regions are defined, you will
        be able to create a rectangular lattice from a selected pin cell and then make individual selections
        to replace those cell regions for which you would prefer a different configuration.  
           """),

    ################################################################################
    html.H3('Cells'),

    html.Div([
        html.Div([
            html.H6("List of Planes"),
            dcc.Input(id='planes-list', value='.45, .4',
                      placeholder='Enter list of radial planes (comma separated)',
                      type="text", style=dict(height=36)),
        ],
            style=dict(
                display='table-cell',
                verticalAlign="top",
                width='10%'
            ),
        ),

        html.Div([
            html.H6("List of Materials"),
            # TODO: Remove these options once app is complete
            dcc.Dropdown(id='material-dropdown', multi=True,
                         options=[{'label': 'Material1', 'value': 'Material1'},
                                  {'label': 'Material2', 'value': 'Material2'},
                                  {'label': 'Material3', 'value': 'Material3'}],
                         value=['Material1', 'Material2', 'Material3']),
            dcc.Graph(id='cell-graph'),
            dcc.Input(id='cell-name', placeholder='Enter Cell Name',
                      type='text'),
            html.Button('Commit Configuration to Memory', id='store-cell-button'),
        ],
            style=dict(
                width='70%',
                display='table-cell',
                verticalAlign="top",
            ),
        ),

        html.Div([
            html.H6("List of Colors"),
            dcc.Dropdown(id='colors-dropdown', multi=True,
                         value=['rgb(255, 0, 0)', 'rgb(25, 255, 0)', 'rgb(0, 22, 255)']),
            daq.ColorPicker(
                id='color-picker',
                label="Material Color",
                value={'hex': '#ff0000', 'rgb': {'r': 255, 'g': 0, 'b': 0, 'a': 1}}
            ),
            dcc.Input(id='color-name', placeholder='Color Name', type="text", size=26),
            html.Button('Add color to Dropdown', id='add-color-button', n_clicks=0),
        ],
            style=dict(
                width='20%',
                display='table-cell',
                verticalAlign="top",
            ),
        ),
    ], style=dict(
        width='100%',
        display='table',
    ),
    ),
    html.Div(style=dict(height=30)),

    ################################################################################
    html.H3('Assemblies'),
    html.P("""
        Now that a cell has been successfully created, it is now available for selection in the 
        dropdown below. The selection made from this cell will create an assembly based on the specifications
        of the selected cell. Don't worry, you will be able to pick and choose individual cells to change 
        their specifications if needed e.g. control rods, water holes, etc. A little description on how to do this:
        Locations of selected cells will be displayed someplace below - this is your main guide when inserting 
        cell universes into the assembly. Keeping track of this information is important because it does not reset once
        an injection is made and this may initially seem a bit unintuitive. Your first step is to make a selection. 
        By clicking on a cell universe multiple times, you may select and deselect the universe from your list of 
        indices. Once you are content with the selection you have made, you may choose what type of cell universe you 
        would like to inject into the chosen indices. You may also "overwrite" other cell universes, i.e. priority is 
        given to your most recent injection. So, if there are indices for cell universes of a type other than your 
        current selection that match your currently selected indices, those indices will be removed from the other cell indices 
        (ones not selected).
           """),
    html.H6('Cell Selection'),
    html.Div([
        html.Div([
            html.Div(style=dict(height=40)),
            html.P("""
                The dropdown below will fill the entire assembly with cells of that type.
                   """),
            dcc.Dropdown(id='cell-dropdown'),
            html.P("X-width Dimension [units]"),
            dcc.Input(id='assembly-x-dimension', placeholder='Enter assembly x-width dimension',
                      type='number', value=15),
            html.P("Y-width Dimension [units]"),
            dcc.Input(id='assembly-y-dimension', placeholder='Enter assembly y-width dimension',
                      type='number', value=15),
            html.P("X-pins [#]"),
            dcc.Input(id='assembly-x-number', placeholder='Enter fuel pins in x-dimension',
                      type='number', value=15),
            html.P("Y-pins [#]"),
            dcc.Input(id='assembly-y-number', placeholder='Enter fuel pins in y-dimension',
                      type='number', value=15),
            html.P("""
                The dropdown below is used to specify the cell type that is to be used to replace
                only the selected cells.
            """),
            dcc.Dropdown(id='injection-cell'),
            html.P("Selected Cells: "), html.Div(id='display-selected'),
            html.Button('Submit cell into selection(s)', id='submit-selected-btn'),
            # TODO: Link to Callback
            html.Div(id='cell-preview'),
        ],
            style=dict(
                width='35%',
                display='table-cell',
                verticalAlign="top",
            ),
        ),
        html.Div(style=dict(
            width='10%',
            display='table-cell',
            verticalAlign="top",
        ),
        ),
        html.Div([
            html.Div(id='assembly-container'),
        ],
            style=dict(
                width='55%',
                display='table-cell',
                verticalAlign="top",
            ),
        )
    ], style=dict(
        width='100%',
        display='table',
    ),
    ),
    dcc.Input(id='assembly-name', placeholder='Enter Assembly Name', size=70, type='text'),
    html.Button('Store Assembly', id='store-assembly-btn', n_clicks=0),
    html.Div(style=dict(height=30)),

    ################################################################################
    html.H3('Boundaries'),
    html.P("""
        In this section you will define the bounds for the simulation. Your model will 
        usually be contained within this defined volume thus the boundaries defined here 
        will larger than any of those previous.
           """),
    html.P('Pick root geometry from Dropdown'),
    dcc.Dropdown(id='root-cell-option'),

    html.Div([
        html.Div([
            html.H6("X Boundaries"),
            html.Br(),
            dcc.RangeSlider(id='boundary-range-x',
                            min=-1000,
                            max=1000,
                            value=[-100, 100],
                            marks={
                                -1000: {'label': '-1000', 'style': {'color': '#77b0b1'}},
                                0: {'label': '0', 'style': {'color': '#f50'}},
                                1000: {'label': '1000', 'style': {'color': '#f50'}}
                            },
                            allowCross=False,
                            pushable=True),
            html.Br(),
            dcc.RadioItems(id='boundary-type-x',
                           options=[
                               {'label': 'Reflective', 'value': 'reflective'},
                               {'label': 'Vacuum', 'value': 'vacuum'},
                           ],
                           value='vacuum'
                           ),
        ],
            style=dict(
                display='table-cell',
                verticalAlign="top",
                width='25%'
            ),
        ),
        html.Div(style=dict(
            display='table-cell',
            verticalAlign="top",
            width='10%'
        )),
        html.Div([
            html.H6("Y Boundaries"),
            html.Br(),
            dcc.RangeSlider(id='boundary-range-y',
                            min=-1000,
                            max=1000,
                            value=[-100, 100],
                            marks={
                                -1000: {'label': '-1000', 'style': {'color': '#77b0b1'}},
                                0: {'label': '0', 'style': {'color': '#f50'}},
                                1000: {'label': '1000', 'style': {'color': '#f50'}}
                            },
                            allowCross=False,
                            pushable=True,
                            ),
            html.Br(),
            dcc.RadioItems(id='boundary-type-y',
                           options=[
                               {'label': 'Reflective', 'value': 'reflective'},
                               {'label': 'Vacuum', 'value': 'vacuum'},
                           ],
                           value='vacuum'
                           ),
        ],
            style=dict(
                display='table-cell',
                verticalAlign="top",
                width='25%'
            ),
        ),
        html.Div(style=dict(
            display='table-cell',
            verticalAlign="top",
            width='10%'
        )),
        html.Div([
            html.H6("Z Boundaries"),
            html.Br(),
            dcc.RangeSlider(id='boundary-range-z',
                            min=-1000,
                            max=1000,
                            value=[-100, 100],
                            marks={
                                -1000: {'label': '-1000', 'style': {'color': '#77b0b1'}},
                                0: {'label': '0', 'style': {'color': '#f50'}},
                                1000: {'label': '1000', 'style': {'color': '#f50'}}
                            },
                            allowCross=False,
                            pushable=True,
                            ),
            html.Br(),
            dcc.RadioItems(id='boundary-type-z',
                           options=[
                               {'label': 'Reflective', 'value': 'reflective'},
                               {'label': 'Vacuum', 'value': 'vacuum'},
                           ],
                           value='vacuum'
                           ),
        ],
            style=dict(
                display='table-cell',
                verticalAlign="top",
                width='25%'
            ),
        ),

    ], style=dict(
        width='100%',
        display='table',
    ),
    ),

    html.Button('Submit Geometrical Boundaries to Memory', id='submit-boundaries-btn')
])


#######################################################################################################################
# Geometry Interface

###########################################
# Commit colors to memory (options state works but trying to debug other errors and cant find source)
@app.callback(
    Output('color-stores', 'data'),
    [Input('add-color-button', 'n_clicks')],
    [State('color-picker', 'value'),
     State('color-name', 'value'),
     State('color-stores', 'data')]
)
def add_color(click, color, name, data):
    data = data or {'options': [{'label': 'Fuel', 'value': 'rgb(255, 0, 0)'},
                                {'label': 'Clad', 'value': 'rgb(25, 255, 0)'},
                                {'label': 'Water', 'value': 'rgb(0, 22, 255)'}]}

    options = data['options']
    color = 'rgb({}, {}, {})'.format(color['rgb']['r'], color['rgb']['g'], color['rgb']['b'])
    if click > 0 and name is not None:
        options.append({'label': name, 'value': color})

    return data


# Populate from Dropdown
@app.callback(
    Output('colors-dropdown', 'options'),
    [Input('color-stores', 'modified_timestamp')],
    [State('color-stores', 'data')]
)
def add_data(timestamp, data):
    if timestamp is None:
        raise PreventUpdate

    if data:
        return data['options']


###########################################


# Graph Cell from Inputs
@app.callback(
    Output('cell-graph', 'figure'),
    [Input('planes-list', 'value'),
     Input('material-dropdown', 'value'),
     Input('colors-dropdown', 'value')],
)
def create_cell(planes, materials, colors):
    planes = [float(plane) for plane in planes.split(',')]
    planes.sort()

    edge = planes[-1] + 0.25 * planes[-1]
    visible_edge = planes[-1] + 0.1 * planes[-1]
    x = np.linspace(-edge, edge, 250)
    y = np.linspace(-edge, edge, 250)

    values = [0]
    colorscale = [[0, 'rgb(255, 255, 255)']]
    if colors is not None and len(colors) >= 1:
        values = np.linspace(0, 1, len(colors) + 1)[1:]
        for value in range(len(colors)):
            colorscale.append([values[value], colors[value]])

    regions = []
    cell_hover = []
    for i in x:
        row = []
        text_row = []
        for j in y:

            if np.sqrt(i ** 2 + j ** 2) < planes[0]:
                # For HoverText
                if materials is None:
                    text_row.append('Region 1')
                else:
                    text_row.append(materials[0])

                # For Color
                if colors is not None:
                    row.append(values[0])
                else:
                    row.append(0)

            if np.sqrt(i ** 2 + j ** 2) > planes[-1]:
                # For HoverText
                if materials is not None and len(materials) > len(planes):
                    text_row.append(materials[-1])
                else:
                    text_row.append('Region {}'.format(len(planes) + 1))

                # For Colors
                if -visible_edge < i < visible_edge and -visible_edge < j < visible_edge:
                    if colors is not None and len(colors) > len(planes):
                        row.append(values[-1])
                    else:
                        row.append(0)
                else:
                    row.append(0)

            for k in range(len(planes) - 1):
                # For HoverText
                if planes[k] < np.sqrt(i ** 2 + j ** 2) < planes[k + 1]:
                    if materials is not None and len(materials) > 1:
                        text_row.append(materials[k + 1])
                    else:
                        text_row.append('Region {}'.format(k + 2))

                # For Colors
                if planes[k] < np.sqrt(i ** 2 + j ** 2) < planes[k + 1]:
                    if colors is not None and len(colors) > 1:
                        row.append(values[k + 1])
                    else:
                        row.append(0)

        regions.append(row)
        cell_hover.append(text_row)

    heatmap = go.Heatmap(z=regions,
                         x=x,
                         y=y,
                         hoverinfo='x+y+text',
                         text=cell_hover,
                         colorscale=colorscale,
                         opacity=0.6,
                         showscale=False)

    shapes = []
    for plane in planes:
        shape = {
            'type': 'circle',
            'x0': -plane,
            'y0': -plane,
            'x1': plane,
            'y1': plane,
            'line': {
                'width': 4,
            },
            'opacity': 1
        }

        shapes.append(shape)

    layout = dict(title='Cell Region Depiction',
                  xaxis=dict(fixedrange=True,
                             range=[-visible_edge, visible_edge]),
                  yaxis=dict(fixedrange=True,
                             range=[-visible_edge, visible_edge]),
                  height=500,
                  width=500,
                  shapes=shapes)

    figure = dict(data=[heatmap], layout=layout)

    return figure


# Commit Cell to memory
@app.callback(
    Output('cell-stores', 'data'),
    [Input('store-cell-button', 'n_clicks')],
    [State('cell-name', 'value'),
     State('planes-list', 'value'),
     State('material-dropdown', 'value'),
     State('colors-dropdown', 'value'),
     State('cell-stores', 'data')]
)
def store_cell(clicks, name, planes, materials, colors, data):
    if clicks is None:
        raise PreventUpdate

    planes = [float(plane) for plane in planes.split(',')]
    planes.sort()

    data = data or {}
    data.update({'{}'.format(name): {'radii': planes,
                                     'materials': materials,
                                     'colors': colors}})

    return data


# Disable Button to commit cell to memory if missing Information
# @app.callback(
#     Output('store-cell-button', 'disabled'),
#     [Input('cell-name', 'value'),
#      Input('planes-list', 'value'),
#      Input('material-dropdown', 'value')]
# )
# def disable_button(name, planes, materials):
#     if planes is None:
#         print("Must have at least one plane")
#     else:
#         planes = [float(plane) for plane in planes.split(',')]
#         planes.sort()
#
#     if len(planes) > 0 and materials is not None and len(materials) == len(planes) + 1 and name is not None:
#         return False
#     else:
#         return True


@app.callback(
    Output('cell-dropdown', 'options'),
    [Input('cell-stores', 'modified_timestamp')],
    [State('cell-stores', 'data')]
)
def populate_dropdown(timestamp, data):
    if timestamp is None:
        raise PreventUpdate

    if data:
        labels = data.keys()
        options = [{'label': label, 'value': label} for label in labels]

        return options


@app.callback(
    Output('injection-cell', 'options'),
    [Input('cell-stores', 'modified_timestamp'),
     Input('cell-dropdown', 'value')],
    [State('cell-stores', 'data')]
)
def populate_dropdown(timestamp, main_cell, data):
    if timestamp is None:
        raise PreventUpdate

    if data:
        labels = data.keys()
        options = [{'label': label, 'value': label} for label in labels]
        if {'label': main_cell, 'value': main_cell} in options:
            options.remove({'label': main_cell, 'value': main_cell})

        return options


#######################################################################################################################
# Assemblies


@app.callback(
    Output('display-selected', 'children'),
    [Input('injection-stores', 'modified_timestamp')],
    [State('injection-stores', 'data')]
)
def show_selection_locations(timestamp, data):
    if timestamp is None:
        raise PreventUpdate

    if data:
        return html.P('{}'.format(str(data['selected-cells'])))


@app.callback(
    Output('injection-stores', 'data'),
    [Input('assembly-graph', 'clickData')],
    [State('injection-stores', 'data')]
)
def print_selected_cells(clickData, data):
    data = data or {'selected-cells': []}
    selected_cells = data['selected-cells']

    if clickData:
        x = clickData['points'][0]['x']
        y = clickData['points'][0]['y']
        if [x, y] not in selected_cells:
            selected_cells.append([x, y])
        else:
            selected_cells.remove([x, y])

    return {'selected-cells': selected_cells}


@app.callback(
    Output('temp-assembly-stores', 'data'),
    [Input('submit-selected-btn', 'n_clicks'),
     Input('cell-dropdown', 'value'),
     Input('assembly-x-dimension', 'value'),
     Input('assembly-y-dimension', 'value'),
     Input('assembly-x-number', 'value'),
     Input('assembly-y-number', 'value')],
    [State('injection-cell', 'value'),
     State('injection-stores', 'data'),
     State('temp-assembly-stores', 'data')]
)
def configure_stores(clicks, main_cell, assembly_dim_x, assembly_dim_y, assembly_num_x, assembly_num_y, selected_cell,
                     selection_locs, data):
    data = data or {'main-cell': {}, 'injected-cells': {}, 'assembly-metrics': {}}
    cells = data['injected-cells']

    data['main-cell'] = main_cell
    data['assembly-metrics']['assembly-dim-x'] = assembly_dim_x
    data['assembly-metrics']['assembly-dim-y'] = assembly_dim_y
    data['assembly-metrics']['assembly-num-x'] = assembly_num_x
    data['assembly-metrics']['assembly-num-y'] = assembly_num_y

    if clicks and selected_cell:

        # If there is no entry at all for selections of specified cell type
        if selected_cell not in cells.keys():
            cells.update({'{}'.format(selected_cell): {'indices': selection_locs['selected-cells']}})

        # Else need to loop thru indices of existing cell types to check duplicated indices
        cells[selected_cell]['indices'] = selection_locs['selected-cells']

        for k in range(len(cells[selected_cell]['indices'])):
            # If the indices are in any of the cells not selected
            cells_list = list(cells.keys())
            for i in range(len(cells_list)):
                if selected_cell != cells_list[i]:

                    if cells[selected_cell]['indices'][k] in cells[cells_list[i]]['indices']:
                        # Remove those indices from that cell
                        cells[cells_list[i]]['indices'].remove(cells[selected_cell]['indices'][k])

    print(data)
    return data


@app.callback(
    Output('assembly-container', 'children'),
    [Input('cell-stores', 'data'),
     Input('temp-assembly-stores', 'data')],
)
def fill_assembly(data, assembly_data):
    main_cell = assembly_data['main-cell']

    if data and main_cell:
        assembly_dim_x = assembly_data['assembly-metrics']['assembly-dim-x']
        assembly_dim_y = assembly_data['assembly-metrics']['assembly-dim-y']
        assembly_num_x = assembly_data['assembly-metrics']['assembly-num-x']
        assembly_num_y = assembly_data['assembly-metrics']['assembly-num-y']

        pitch_x = assembly_dim_x / assembly_num_x
        pitch_y = assembly_dim_y / assembly_num_y

        # if planes[0] * assembly_num_x > assembly_dim_x or planes[0] * assembly_num_y > assembly_dim_y:
        #     return html.P("Assembly Dimensions and/or Quantities are insensible. You will see this message"
        #                   "if your specifications are causing pins to overlap!")
        # else:

        shapes = []
        assembly_hover = []
        for a in range(assembly_num_y):
            row = []
            for b in range(assembly_num_x):
                row.append('{}'.format(main_cell))

                if assembly_data:
                    # If index is not specified in any of cell indices
                    if [b, a] not in [result for cell_name in assembly_data['injected-cells'].keys() for result in
                                      assembly_data['injected-cells'][cell_name]['indices']]:

                        planes = data[main_cell]['radii']
                        planes = planes[::-1]

                        colors = data[main_cell]['colors']
                        colors = colors[::-1][1:]

                        for p in range(len(planes)):
                            color = colors[p]
                            shape = {
                                'type': 'circle',
                                'x0': b - planes[p] / pitch_x / 2,
                                'y0': a - planes[p] / pitch_y / 2,
                                'x1': b - planes[p] / pitch_x / 2 + planes[p] / pitch_x,
                                'y1': a - planes[p] / pitch_y / 2 + planes[p] / pitch_y,
                                'fillcolor': color,
                                'line': dict(width=.1),
                                'opacity': 1
                            }
                            shapes.append(shape)

                    # Index is
                    else:
                        for cell_name in assembly_data['injected-cells'].keys():
                            if [b, a] in assembly_data['injected-cells'][cell_name]['indices']:
                                planes = data[cell_name]['radii']
                                planes = planes[::-1]

                                colors = data[cell_name]['colors']
                                colors = colors[::-1][1:]

                                for p in range(len(planes)):
                                    color = colors[p]
                                    shape = {
                                        'type': 'circle',
                                        'x0': b - planes[p] / pitch_x / 2,
                                        'y0': a - planes[p] / pitch_y / 2,
                                        'x1': b - planes[p] / pitch_x / 2 + planes[p] / pitch_x,
                                        'y1': a - planes[p] / pitch_y / 2 + planes[p] / pitch_y,
                                        'fillcolor': color,
                                        'line': dict(width=.1),
                                        'opacity': 1
                                    }
                                    shapes.append(shape)

                else:
                    planes = data[main_cell]['radii']
                    planes = planes[::-1]

                    colors = data[main_cell]['colors']
                    colors = colors[::-1][1:]

                    for p in range(len(planes)):
                        color = colors[p]
                        shape = {
                            'type': 'circle',
                            'x0': b - planes[p] / pitch_x / 2,
                            'y0': a - planes[p] / pitch_y / 2,
                            'x1': b - planes[p] / pitch_x / 2 + planes[p] / pitch_x,
                            'y1': a - planes[p] / pitch_y / 2 + planes[p] / pitch_y,
                            'fillcolor': color,
                            'line': dict(width=.1),
                            'opacity': 1
                        }
                        shapes.append(shape)

            assembly_hover.append(row)

        # Invert Matrices
        assembly_hover = assembly_hover[::-1]
        assembly_region = np.ones((assembly_num_y, assembly_num_x))
        colorscale = [[0, 'rgb(255, 255, 255)'], [1, data[main_cell]['colors'][-1]]]
        radius = data[main_cell]['radii'][::-1][0]

        layout = dict(
            title='Assembly Depiction',
            height=750,
            width=750,

            xaxis=dict(
                range=[-(radius / 2 + (pitch_x - radius) / 2), assembly_num_x],
                zeroline=False,
                fixedrange=True
            ),
            yaxis=dict(
                range=[-(radius / 2 + (pitch_y - radius) / 2), assembly_num_y],
                zeroline=False,
                fixedrange=True
            ),
            shapes=shapes,
        )

        heatmap = go.Heatmap(z=assembly_region,
                             hoverinfo='x+y+text',
                             text=assembly_hover,
                             colorscale=colorscale,
                             showscale=False,
                             opacity=1)
        data = [heatmap]

        figure = dict(data=data, layout=layout)

        return dcc.Graph(id='assembly-graph', figure=figure)


# TODO: Support multiple assemblies to create universe dropdown
# @app.callback(
#     Output('assembly-stores', 'data'),
#     [Input('store-assembly-btn', 'n_clicks')],
#     [State('assembly-name', 'value'),
#      State('temp-assembly-stores', 'data'),
#      State('assembly-stores', 'data')]
# )
# def store_to_assemblies(click, assembly_name, assembly_data, all_assembly_data):
#     all_assembly_data = all_assembly_data or {}
#
#     if click:
#         all_assembly_data.update({'{}'.format(assembly_name):
#                                       {}
#                                   })

#######################################################################################################################
# Full-Core
# TODO


#######################################################################################################################
# Boundaries

# Store whole-geometry outer boundary and type
@app.callback(
    Output('boundary-stores', 'data'),
    [Input('submit-boundaries-btn', 'n_clicks')],
    [State('boundary-range-x', 'value'),
     State('boundary-range-y', 'value'),
     State('boundary-range-z', 'value'),
     State('boundary-type-x', 'value'),
     State('boundary-type-y', 'value'),
     State('boundary-type-z', 'value'),
     State('boundary-stores', 'data')])
def set_boundaries(clicks, range_x, range_y, range_z, btype_x, btype_y, btype_z, boundary_data):
    boundary_data = boundary_data or {}
    if clicks:
        min_x = range_x[0]
        max_x = range_x[1]
        min_y = range_y[0]
        max_y = range_y[1]
        min_z = range_z[0]
        max_z = range_z[1]

        boundary_data.update({'X-min': min_x, 'X-max': max_x, 'X-btype': btype_x,
                              'Y-min': min_y, 'Y-max': max_y, 'Y-btype': btype_y,
                              'Z-min': min_z, 'Z-max': max_z, 'Z-btype': btype_z})

    return boundary_data
