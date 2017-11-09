import pandas as pd
import scripts as s
import numpy as np
from bokeh.io import curdoc
from bokeh.plotting import figure, ColumnDataSource, output_notebook, output_file, show, save
from bokeh.models import HoverTool, WheelZoomTool, PanTool, BoxZoomTool, ResetTool, TapTool, SaveTool
from bokeh.palettes import brewer
from bokeh.models.widgets import Dropdown, Select, MultiSelect, Button, CheckboxButtonGroup
from bokeh.layouts import row, widgetbox, column

# Loads the dataframe
data_all = pd.read_pickle('./data_small')
# Sets the alpha level for the hidden points
alpha = np.ones((data_all.shape[0]))*.1
# creates a dataframe for the hidden points
alpha_df = pd.DataFrame(alpha, columns=['alpha'], index=data_all.index)
# Merges the dataframe
data_all = pd.concat([data_all, alpha_df], axis=1)

# finds all the catagories
category_items = data_all['System'].unique()



names = s.generate_names_from_list(category_items)

elements = data_all['System'].str.findall('[A-Z][^A-Z]*')
elements = pd.DataFrame(elements.values.tolist(), columns = ['A_cation','B_cation','Oxygen'])

a_names = s.generate_names_from_list(elements['A_cation'].unique())
b_names = s.generate_names_from_list(elements['B_cation'].unique())

# Randomly selects the colors
palette = []
for i in range(len(category_items)):
    palette = np.append(palette, "#%06x" % np.random.randint(0, 0xFFFFFF))

# if there are a low number of examples brewer can be used to define the colors.
# If not
#palette = brewer['Set3'][len(category_items) + 1]
colormap = dict(zip(category_items, palette))
data_all['color'] = data_all['System'].map(colormap)
test_ind = np.load('test_set.npy')

# Splits the arrays based on the atoms
elements = data_all['System'].str.findall('[A-Z][^A-Z]*')
elements = pd.DataFrame(elements.values.tolist(), columns = ['A_cation','B_cation','Oxygen'])

def get_dataset(src,test_ind, update=' ', type=' '):
    df = src.copy()
    if select_data_box.value == "All":
        df = df
    elif select_data_box.value  == "Test":
        df = df.iloc[test_ind]
    else:
        df = df.iloc[~test_ind]

    if type is "chemistry":
        df.loc[df['System'].isin(update),('alpha')] = 1

        if show_all_or_selected.value == "selected":
            df = df.loc[df['System'].isin(update)]

    return ColumnDataSource(data=df)

def make_plot(source):
    hover = HoverTool(tooltips=[(column, '@' + column) for column in ['System',
                                                                      'lattice_a', 'lattice_b', 'lattice_c']])

    tools = [hover, WheelZoomTool(), PanTool(), BoxZoomTool(), ResetTool(), TapTool(), SaveTool()]

    p = figure(
        tools=tools,
        # title=title,
        plot_width=1600,
        plot_height=1600,
        toolbar_location='below',
        toolbar_sticky=False, )

    p.circle(
        x='Component 1',
        y='Component 2',
        source=source,
        size=10,
        line_color='#333333',
        line_width=0.5,
        alpha='alpha',
        color='color',
        # legend=category
    )

    return p

def update_plot(attrname, old, new):
    src = get_dataset(data_all, test_ind, multi_select.value)
    source.data.update(src.data)

def update_plot_chemistry(attrname, old, new):
    src = get_dataset(data_all, test_ind, multi_select.value, 'chemistry')
    source.data.update(src.data)

def update_plot_a_or_b(attrname, old, new):
    matching = []
    for i in multi_select_A_cation.value:
        matching = np.append(matching,[s for s in category_items if i in s])

    matching_= []
    for i in multi_select_B_cation.value:
        matching_ = np.append(matching_,[s for s in matching if i in s])


    multi_select.value = np.ndarray.tolist(matching_)

def reset_plot():
    src = get_dataset(data_all, test_ind,type='reset')
    source.data.update(src.data)


select_data_box = Select(title="Data to Include:", value="All", options=["All", "Test", "Train"])

multi_select = MultiSelect(title="Chemistries:", value=np.ndarray.tolist(category_items),
                           options=names, size = 12)

multi_select_A_cation = MultiSelect(title="A-Site Cation:", value=np.ndarray.tolist(elements['A_cation'].unique()),
                           options=a_names, size = 12)

multi_select_B_cation = MultiSelect(title="B-Site Cation:", value=np.ndarray.tolist(elements['B_cation'].unique()),
                           options=b_names, size = 12)

show_all_or_selected = Select(title="Show all data or selected:", value="All", options=["All", "selected"])

Reset_button = Button(label='Reset', button_type='warning')

source = get_dataset(data_all,test_ind, select_data_box.value, multi_select.value)

p = make_plot(source)

select_data_box.on_change('value', update_plot)
multi_select.on_change('value', update_plot_chemistry)
multi_select_A_cation.on_change('value', update_plot_a_or_b)
multi_select_B_cation.on_change('value', update_plot_a_or_b)
Reset_button.on_click(reset_plot)

#select_data_box.on_change('value', update_plot)

#inputs = widgetbox(*controls)
selections = column(row(select_data_box, show_all_or_selected) ,multi_select,
                                row(multi_select_A_cation, multi_select_B_cation),
                                Reset_button)
curdoc().add_root(row(selections, p))
curdoc().title = "Weather"

#show()
