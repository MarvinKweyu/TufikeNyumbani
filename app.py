from flask import Flask, render_template, request
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.transform import linear_cmap
from bokeh.palettes import Spectral6
from bokeh.models.annotations import ColorBar


app = Flask(__name__)

# load dataset
fatalities = pd.read_csv('./data/clean_data.csv')


""" 
Items to generate:
1.Fatalities per year and how it is changing over time
2.Fatalities per state
3.Fatalities at different times of the day
4.Impact of different speed limit zones
5.Impact of different road-user roles: driver,passenger, motor_cyclist
"""
items_for_compare = ['Year', 'State', 'Month']


# def create_figure(according_to,hover_tool=None):
def create_figure(according_to):
    """Create main plot. """
    # group by category selected
    fatalities[according_to] = fatalities[according_to].astype(str)
    group = fatalities.groupby(according_to)
    source = ColumnDataSource(group)

    if according_to == "Year":
        TOOLTIPS = [
            ('Fatalities', '$y'),
        ]
    else:
        TOOLTIPS = None

    plot = figure(plot_height=600, plot_width=900, x_range=group,
                  title=f"\nFatalities according to {according_to}", tooltips=TOOLTIPS, y_axis_label="Road Fatality count", x_axis_label=f"{according_to}")
    plot.title.text_font_size = '13pt'
    plot.title.align = 'center'

    if according_to == 'Year':
        plot.line(x='Year', y='Age_count', line_width=2, source=source)
    elif according_to == "State":
        plot.vbar(x='State', top='Age_count', width=0.8, source=source)
       
    else:
         # Use the field name of the column source
        mapper = linear_cmap(field_name='Age_count', palette=Spectral6 ,low=min(source.data['Age_count']) ,high=max(source.data['Age_count']))
      
        plot.circle(x='Month', y='Age_count',line_color=mapper,color=mapper, fill_alpha=1, size=12,source=source)

        color_bar = ColorBar(color_mapper=mapper['transform'], width=8,  location=(0,0))

        plot.add_layout(color_bar, 'right')

    plot.toolbar.logo = None
    plot.toolbar.autohide = True

    hover = plot.select(dict(type=HoverTool))
    hover.mode = 'vline'  # hover mode to year

    return plot


def create_hover():
    """Create a hover tool.
    ? Dependent tooltips
    """

    hover_html = """
    <div>
        <span class="hover-tooltip>$x</span>
    <div>
    # if hover_tool:
    #     tools = [hover_tool]

     <div>
        <span class="hover-tooltip>@Age_count fatalities</span>
    <div>

     <div>
        <span class="hover-tooltip>$x</span>
    <div>
     """

    return HoverTool(tooltips=hover_html)


@app.route('/')
def index():

    # determine selected feature
    current_comparison = request.args.get("item_for_compare")
    if current_comparison == None:
        current_comparison = "Year"

    # hover_tool = create_hover()
    # create plot
    plot = create_figure(current_comparison)

    # embed plot to html
    script, div = components(plot)

    return render_template("index.html", script=script, div=div, the_items_for_compare=items_for_compare, current_comparison=current_comparison)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
