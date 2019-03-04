import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input

import plotly.graph_objs as go

import openmc
import openmc.model
import openmc.mgxs

import numpy as np
import re
import pickle
import redis

# Add Periodic Table Data
element = [['Hydrogen', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Helium'],
           ['Lithium', 'Beryllium', '', '', '', '', '', '', '', '', '', '', 'Boron', 'Carbon', 'Nitrogen', 'Oxygen',
            'Fluorine', 'Neon'],
           ['Sodium', 'Magnesium', '', '', '', '', '', '', '', '', '', '', 'Aluminium', 'Silicon', 'Phosphorus',
            'Sulfur', 'Chlorine', ' Argon'],
           ['Potassium', ' Calcium', ' Scandium', ' Titanium', ' Vanadium', ' Chromium', 'Manganese', 'Iron', 'Cobalt',
            'Nickel', 'Copper', 'Zinc', 'Gallium', 'Germanium', 'Arsenic', 'Selenium', 'Bromine', 'Krypton'],
           ['Rubidium', 'Strontium', 'Yttrium', 'Zirconium', 'Niobium', 'Molybdenum', 'Technetium', 'Ruthenium',
            'Rhodium', 'Palladium', 'Silver', 'Cadmium', 'Indium', 'Tin', 'Antimony', 'Tellurium', 'Iodine', 'Xenon'],
           [' Cesium', ' Barium', '', 'Hafnium', 'Tantalum', 'Tungsten', 'Rhenium', 'Osmium', 'Iridium', 'Platinum',
            'Gold', 'Mercury', 'Thallium', 'Lead', 'Bismuth', 'Polonium', 'Astatine', 'Radon'],
           [' Francium', ' Radium', '', 'Rutherfordium', 'Dubnium', 'Seaborgium', 'Bohrium', 'Hassium', 'Meitnerium',
            'Darmstadtium', 'Roentgenium', 'Copernicium', 'Ununtrium', 'Ununquadium', 'Ununpentium', 'Ununhexium',
            'Ununseptium', 'Ununoctium'],
           ['', '', 'Lanthanum', 'Cerium', 'Praseodymium', 'Neodymium', 'Promethium', 'Samarium', 'Europium',
            'Gadolinium', 'Terbium', 'Dysprosium', 'Holmium', 'Erbium', 'Thulium', 'Ytterbium', 'Lutetium', ''],
           ['', '', 'Actinium', 'Thorium', 'Protactinium', 'Uranium', 'Neptunium', 'Plutonium', 'Americium', 'Curium',
            'Berkelium', 'Californium', 'Einsteinium', 'Fermium', 'Mendelevium', 'Nobelium', 'Lawrencium', ''], ]

symbol = [['H', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'He'],
          ['Li', 'Be', '', '', '', '', '', '', '', '', '', '', 'B', 'C', 'N', 'O', 'F', 'Ne'],
          ['Na', 'Mg', '', '', '', '', '', '', '', '', '', '', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar'],
          ['K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr'],
          ['Rb ', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe'],
          ['Cs', 'Ba', '', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn'],
          ['Fr', 'Ra', '', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Uut', 'Fl', 'Uup', 'Lv', 'Uus',
           'Uuo'],
          ['', '', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', ''],
          ['', '', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', '']]

atomic_number = [['1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '2'],
                 ['3', '4', '', '', '', '', '', '', '', '', '', '', '5', '6', '7', '8', '9', '10'],
                 ['11', '12', '', '', '', '', '', '', '', '', '', '', '13', '14', '15', '16', '17', '18'],
                 ['19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35',
                  '36'],
                 ['37 ', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53',
                  '54'],
                 ['55', '56', '', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85',
                  '86'],
                 ['87', '88', '', '104', '105', '106', '107', '108', '109', '110', '111', '112', '113', '114', '115',
                  '116', '117', '118'],
                 ['', '', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', ''],
                 ['', '', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '100', '101', '102', '103',
                  '']]

atomic_mass = [[1.00794, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, 4.002602],
               [6.941, 9.012182, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, 10.811, 12.0107, 14.0067, 15.9994, 18.9984032,
                20.1797],
               [22.98976928, 24.3050, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, 26.9815386, 28.0855, 30.973762, 32.065,
                35.453, 39.948],
               [39.0983, 40.078, 44.955912, 47.867, 50.9415, 51.9961, 54.938045, 55.845, 58.933195, 58.6934, 63.546,
                65.38, 69.723, 72.64, 74.92160, 78.96, 79.904, 83.798],
               [85.4678, 87.62, 88.90585, 91.224, 92.90638, 95.96, 98, 101.07, 102.90550, 106.42, 107.8682, 112.411,
                114.818, 118.710, 121.760, 127.60, 126.90447, 131.293],
               [132.9054519, 137.327, .0, 178.49, 180.94788, 183.84, 186.207, 190.23, 192.217, 195.084, 196.966569,
                200.59, 204.3833, 207.2, 208.98040, 209, 210, 222],
               [223, 226, .0, 267, 268, 271, 272, 270, 276, 281, 280, 285, 284, 289, 288, 293, 'unknown', 294],
               [.0, .0, 138.90547, 140.116, 140.90765, 144.242, 145, 150.36, 151.964, 157.25, 158.92535, 162.500,
                164.93032, 167.259, 168.93421, 173.054, 174.9668, .0],
               [.0, .0, 227, 232.03806, 231.03588, 238.02891, 237, 244, 243, 247, 247, 251, 252, 257, 258, 259, 262,
                .0], ]

z = [[.8, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, 1.],
     [.1, .2, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .7, .8, .8, .8, .9, 1.],
     [.1, .2, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .6, .7, .8, .8, .9, 1],
     [.1, .2, .3, .3, .3, .3, .3, .3, .3, .3, .3, .3, .6, .7, .8, .8, .9, 1.],
     [.1, .2, .3, .3, .3, .3, .3, .3, .3, .3, .3, .3, .6, .6, .7, .7, .9, 1.],
     [.1, .2, .4, .3, .3, .3, .3, .3, .3, .3, .3, .3, .6, .6, .6, .7, .9, 1.],
     [.1, .2, .5, .3, .3, .3, .3, .3, .3, .3, .3, .3, .6, .6, .6, .6, .9, 1.],
     [.0, .0, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .0],
     [.0, .0, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .0], ]

# Display element name and atomic mass on hover
hover = []
for a in range(len(symbol)):
    hover.append(
        [i + ': ' + j + '<br>' + 'Atomic Mass: ' + str(k) for i, j, k in zip(symbol[a], element[a], atomic_mass[a])])

# Invert Matrices
symbol = symbol[::-1]
atomic_number = atomic_number[::-1]
hover = hover[::-1]
z = z[::-1]

x = np.arange(np.shape(z)[1])
y = np.arange(np.shape(z)[0])

# Set Colorscale
colorscale = [[0.0, 'rgb(255,255,255)'], [.1, 'rgb(87, 27, 103)'],
              [.2, 'rgb(65, 69, 133)'], [.3, 'rgb(55, 96, 139)'],
              [.4, 'rgb(46, 120, 141)'], [.5, 'rgb(41, 145, 139)'],
              [.6, 'rgb(45, 167, 133)'], [.7, 'rgb(74, 189, 115)'],
              [.8, 'rgb(126, 207, 89)'], [.9, 'rgb(189, 216, 88)'],
              [1.0, 'rgb(252, 229, 64)']]

annotations = []
for n in range(np.shape(z)[0]):
    for m in range(np.shape(z)[1]):
        annotations.append(go.layout.Annotation(text=str(symbol[n][m]), x=x[m], y=y[n],
                                                xref='x1', yref='y1', showarrow=False,
                                                font=dict(family='Courier New',
                                                          size=20,
                                                          color='black')))

        annotations.append(go.layout.Annotation(text=str(atomic_number[n][m]), x=x[m] + .3, y=y[n] + .3,
                                                xref='x1', yref='y1', showarrow=False,
                                                font=dict(family='Courier New',
                                                          size=15,
                                                          color='black')
                                                ))

heatmap = go.Heatmap(x=x, y=y, z=z, hoverinfo='text', text=hover, colorscale=colorscale, showscale=False, opacity=.5)

data = [heatmap]

periodic_table = go.Figure(data=data)
periodic_table['layout'].update(
    title="Periodic Table of Elements",
    annotations=annotations,
    xaxis=dict(zeroline=False, showgrid=False, showticklabels=False, ticks='', ),
    yaxis=dict(zeroline=False, showgrid=False, showticklabels=False, ticks='', ),
    width=1250,
    height=750,
    autosize=False
)

app = dash.Dash()
app.config['suppress_callback_exceptions'] = True

#######################################################################################################################

app.layout = html.Div([
    ################################################################################
    # Title
    html.H2('Cross Section Configuration',
            style={
                'position': 'relative',
                'top': '0px',
                'left': '10px',
                'font-family': 'Dosis',
                'display': 'inline',
                'font-size': '4.0rem',
                'color': '#4D637F'
            }),

    ################################################################################
    html.Br(),

    # Periodic Table for Material Selection
    html.Div([
        html.Button('Configure Cross-sections', id='config-xs-button', n_clicks=0),
        html.Div(id='xs-config-container'),
    ]),

])
#######################################################################################################################
# Initialize model & redisworks for memory sharing between callbacks
r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.flushall()


def store_object(key, obj):
    var = pickle.dumps(obj)
    r.set(key, var)


def restore_object(key):
    obj = pickle.loads(r.get(key))
    return obj


store_object('model', openmc.model.Model())

############################################################################################################
# Cross-Section Interface
mgxs_lib = openmc.mgxs.Library(restore_object('model').geometry)


@app.callback(
    Output('xs-config-container', 'children'),
    [Input('config-xs-button', 'n_clicks')], )
def invoke_xs_options(n_clicks):
    if n_clicks > 0:
        options = html.Div([
            html.Label('Number of Energy Groups'),
            html.Br(),
            dcc.Slider(
                id='energy-group-input',
                min=0,
                max=100,
                step=1,
                value=5,
                marks={i: i for i in range(0, 100, 5)},
            ),
            html.Br(),
            html.Label('Select mesh to apply to cross-section calculations'),
            html.A(id='cross-section-message'),
        ])

        return options


# TODO: import mesh into function
@app.callback(
    Output('cross-section-message', 'children'),
    [Input('energy-group-input', 'value'),
     Input('mesh-dropdown', 'value')],
)
def build_xs_library(groups, meshes):
    energy_groups = openmc.mgxs.EnergyGroups()
    # TODO: Make sure the groups+1 is accurate
    energy_groups.group_edges = np.logspace(-3, 7.3, groups + 1)

    # Instantiate a 1-group EnergyGroups object
    # one_group = openmc.mgxs.EnergyGroups()
    # one_group.group_edges = np.array([energy_groups.group_edges[0], energy_groups.group_edges[-1]])

    mgxs_lib.energy_groups = energy_groups
    # TODO: Get user-specified delayed groups
    mgxs_lib.num_delayed_groups = 6

    # Specify multi-group cross section types to compute
    mgxs_lib.mgxs_types = ['total', 'transport', 'nu-scatter matrix', 'kappa-fission', 'inverse-velocity', 'chi-prompt',
                           'prompt-nu-fission', 'chi-delayed', 'delayed-nu-fission', 'beta']
    # Specify a "mesh" domain type for the cross section tally filters
    mgxs_lib.domain_type = 'mesh'

    # Specify the mesh domain(s) over which to compute multi-group cross sections
    for mesh in meshes:
        mgxs_lib.domains.append(mesh)

    # Construct all tallies needed for the multi-group cross section library
    mgxs_lib.build_library()

    message = 'Cross-section library built'

    return message


if __name__ == '__main__':
    app.run_server(debug=True)
