import os, sys, re, hashlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from ipywidgets import *
from ipyleaflet import *
from intervaltree import IntervalTree

import roads_cba_py.cba as cba
from roads_cba_py.cba_result import CbaResult
from roads_cba_py.section import Section


def generate_outputs(df: pd.DataFrame, drop_detail_cols: bool, keep_cols=[]):
    cba_model = cba.CostBenefitAnalysisModel()

    inputs = df.apply(lambda row: Section.from_row(row), axis=1)
    output = [cba_model.compute_cba_for_section(i) for i in inputs]
    output = pd.DataFrame([e.to_dict() for e in output])
    inputs = pd.DataFrame([i.to_dict() for i in inputs])

    if drop_detail_cols:
        cols_to_drop = [e for e in list(output.columns) if re.match(".*_[0-9].*", e) and e not in keep_cols]
        # print(f"dropping: {cols_to_drop}")
        output = output.drop(columns=cols_to_drop)

    map_data = df.merge(output, left_on="way_id_district", right_on="orma_way_id")
    map_data = map_data.merge(
        inputs[["orma_way_id", "roughness", "road_length"]], left_on="way_id_district", right_on="orma_way_id"
    )

    map_data.sort_values(by=["work_year", "npv_cost"], ascending=[True, False], inplace=True)
    map_data["cum_investment"] = np.cumsum(map_data["work_cost"])
    map_data["cum_npv"] = np.cumsum(map_data.npv)

    return map_data


def app(map_gdf):
    header = Output()
    with header:
        display(HTML("<h1>ORMA CBA Analysis Proof of Concept</h1>"))
        display(HTML("<style>h1 { text-align: center; font-size: 30pt }</style>"))

    m, legend = generate_map(map_gdf)
    attr = m.children[1]
    map_ui = m.children[0]
    attr.layout.width = "8%"
    tab_ui = add_tabs(map_gdf)
    map_ui.add_control(legend)

    app = VBox()
    main_ui = HBox()
    main_ui.children = [attr, map_ui, tab_ui]
    app.children = [header, main_ui]
    return app


# def update_sa3_box(feature,  **kwargs):
#     sa3_ = feature['properties']['SA3_NAME16']
#     trips_for_sa3 = survey_by_sa3_and_mode.loc[survey_by_sa3_and_mode.SA3_NAME16 == sa3_]
#     total_trips = trips_for_sa3.trips.sum()

#     html_sa3.value = '''
#         <h3><b>{}</b></h3>
#         <h4>SA4 {}</h4>
#         <h4>trips: {:.2f}</h4>
#     '''.format(feature['properties']['SA3_NAME16'],
#                feature['properties']['SA4_NAME16'],
#                total_trips)
# html_sa3 = HTML('''Hover over a SA''')
# html_sa3.layout.margin = '0px 10px 0px 10px'
# control_sa3 = WidgetControl(widget=html_sa3, position='topright')
# m.add_control(control_sa3)

# sa3_data.on_hover(update_sa3_box)


def generate_map(map_gdf):

    center = (22.770006, 104.984655)
    m = Map(center=center, zoom=10, basemap=basemaps.CartoDB.Positron)
    m.layout.height = "800px"

    attr = HTML("Hover on a link", layout=Layout(width="15%"))
    geo_layer = add_roads(m, map_gdf, attr)
    legend = LegendControl(year_legend, name="Year", position="bottomright")
    m.add_control(legend)

    add_budget(m, map_gdf)
    add_dropdown(m, geo_layer, legend)
    m.add_control(ZoomControl(position="topright"))

    return (HBox([m, attr]), legend)


def add_tabs(map_gdf):

    tab = Tab()
    tab.children = [generate_cumulative_npv(map_gdf), generate_network_stats(map_gdf), generate_priorities(map_gdf)]
    tab.set_title(index=0, title="Cumulative NPV")
    tab.set_title(index=1, title="Network Stats")
    tab.set_title(index=2, title="Budget Effects")
    tab.layout.width = "40%"

    return tab


def generate_priorities(gdf):
    canvas = Output()
    total_budget = sum(gdf.work_cost)

    def update_priorities(change):
        with canvas:
            canvas.clear_output()
            fig, ax = plt.subplots(constrained_layout=True, figsize=(15, 10))
            fig.canvas.toolbar_position = "bottom"
            # ax.grid(True)

            years = [1, 3, 5, 8]
            total_length = sum(gdf.road_length)

            base_iri = [sum(gdf[f"iri_base_{x}"] * gdf["road_length"]) / total_length for x in years]

            def get_threshold_iri(perc):
                threshold = perc * total_budget
                do_df, dont_df = gdf.query("cum_investment < @threshold"), gdf.query("cum_investment >= @threshold")

                do_numbers = [sum(do_df[f"iri_projection_{x}"] * do_df["road_length"]) for x in [1, 3, 5, 8]]
                dont_numbers = [sum(dont_df[f"iri_base_{x}"] * dont_df["road_length"]) for x in [1, 3, 5, 8]]
                return [(x + y) / total_length for x, y in zip(do_numbers, dont_numbers)]

            thresholds = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
            data = {f"{p*100}%": get_threshold_iri(p) for p in thresholds}
            data["year"] = years = [y + 2021 for y in years]
            df = pd.DataFrame(data=data).set_index("year")
            # display(df)
            sns.lineplot(data=df, ax=ax, palette=sns.color_palette("light:#5A9", 6))
            c = sns.color_palette("husl", 9)[7]

            sns.lineplot(
                x=years, y=get_threshold_iri(change["new"] / 100.0), ax=ax, color=c, label=f"Custom: {change['new']}%"
            )

            ax.set_title("Roughness Progression By Percentage Investment", fontsize=18)

            plt.show()
            return None

    # update_cumulative_npv(gdf)

    text_ui = Output()
    with text_ui:
        display(
            HTML(
                f"""
            <div class='budget_label'>The work program generated requires a budget of
                                        ${round(total_budget, 2)}M USD</div>
            <div class='budget_label'>Use the slider below to see the effect on the network of spending only a proportion of that budget.</div>
        """
            )
        )
    display(HTML("<style>.budget_label { color: black; font-size: 12pt }</style>"))

    prop_budget = Output()

    def update_budget_box(change):
        with prop_budget:
            part_budget = change["new"] * total_budget / 100.0
            prop_budget.clear_output()
            display(
                HTML(
                    f"""
              <div class='partial_budget'>Partial Budget: ${round(part_budget, 2)}M USD</div>
            """
                )
            )

    update_budget_box({"new": 90.0})
    display(HTML("<style>.partial_budget { color: black; font-size: 16pt }</style>"))

    slider = FloatSlider(value=90.0, min=0, max=100.0, description="Budget %:", continuous_update=False)
    slider.observe(update_priorities, names="value")
    slider.observe(update_budget_box, names="value")
    update_priorities({"new": 90.0})

    return VBox([text_ui, HBox([slider, prop_budget]), canvas])


def generate_cumulative_npv(gdf):
    canvas = Output()

    def update_cumulative_npv(gdf):

        with canvas:
            canvas.clear_output()
            fig, ax = plt.subplots(constrained_layout=True, figsize=(15, 10))
            fig.canvas.toolbar_position = "bottom"
            ax.grid(True)

            sns.scatterplot(data=gdf, ax=ax, x="cum_investment", y="cum_npv", hue="work_year", palette="husl")
            ax.set_xlabel("Investment $M", fontsize=22)
            ax.set_ylabel("NPV $M", fontsize=2)
            ax.set_title(f"NPV vs Investment", fontsize=2)
            plt.show()
            return None

    update_cumulative_npv(gdf)

    text_ui = Output()
    with text_ui:
        display(
            HTML(
                f"""<div class='text_label'>
            The following plot shows the relative value of investment across the work program duration.
        </div>"""
            )
        )
    display(HTML("<style>.text_label { color: black; font-size: 12pt }</style>"))

    return VBox([text_ui, canvas])


def generate_network_stats(gdf):
    canvas = Output()
    canvas2 = Output()

    def update_network_stats(gdf):

        with canvas:
            canvas.clear_output()
            df = gdf.loc[:, ["roughness", "road_length"]]

            def categorise_roughness(r):
                if r < 2.5:
                    return "<2.5"
                elif r < 4:
                    return "2.5-4.0"
                elif r < 6:
                    return "4.0-6.0"
                elif r < 10:
                    return "6.0-10.0"
                elif r < 14:
                    return "10.0-14.0"
                else:
                    return "14.0+"

            df["roughness_label"] = df["roughness"].apply(categorise_roughness)

            fig, ax = plt.subplots(constrained_layout=True, figsize=(6, 6))
            ax.grid(False)

            # sns.barplot(data=df, ax=ax, x='roughness_label', y='road_length')
            sns.histplot(
                data=df, x="roughness", ax=ax, stat="density", weights="road_length", binrange=(0, 16), bins=16
            )
            ax.set_xlabel("Roughness", fontsize=16)
            ax.set_ylabel("% of Network", fontsize=16)

        with canvas2:
            canvas2.clear_output()

            # Seaborn Horizontal barplot
            df = df.groupby("roughness_label").sum()[["road_length"]].reset_index()
            fig, ax = plt.subplots(constrained_layout=True, figsize=(6, 6))
            plt.pie(
                x=df["road_length"],
                autopct="%.1f%%",
                labels=df["roughness_label"],
                pctdistance=0.5,
                colors=sns.color_palette("Set2", 9),
            )
            ax.set_title("Roughness Distribution", fontsize=16)

            plt.show()
            return None

    update_network_stats(gdf)

    vbox = VBox()
    vbox.children = [canvas, canvas2]
    return vbox


def add_dropdown(m, geo_layer, legend):
    global z_mode
    z_mode = "Work Year"

    color_fns = {
        "Work Year": color_by_year,
        "Relative CBR": color_by_npv_cost,
        "District": color_by_district,
        "IRI": color_by_iri,
    }
    legend_lu = {
        "Work Year": year_legend,
        "Relative CBR": npv_cost_legend,
        "District": district_legend,
        "IRI": iri_legend,
    }

    def on_click_dropdown_options(change):
        global z_mode, z_time
        z_mode = change["new"]
        print(change["new"])
        geo_layer.style_callback = color_fns[change["new"]]
        legend.title = change["new"]
        legend.legend = legend_lu[change["new"]]

        # update_zones_box_comp()

    dropdown_options = Dropdown(
        options=["Work Year", "Relative CBR", "District", "IRI"], value=z_mode, description="Color By"
    )

    dropdown_options.observe(on_click_dropdown_options, "value")
    widget_option = WidgetControl(widget=dropdown_options, position="topright")

    m.add_control(widget_option)


def create_li(desc, value):
    return f"""
        <li>
          <div class='label'>{desc}:</div>
          <div class='value'>{value}</div>
        </li>
    """


# MM_ID': '032HG00001', 'aadt': None, 'condition': '3', 'cum_investment': 595.9695185875752, 'cum_npv': 187.8679445588673, 'district': 'Huyện Hoàng Su Phì', 'eirr': 0.20888198812785586, 'esa_loading': 0.0030787749999999997, 'iri': None, 'iri_base_1': 6, 'iri_base_10': 2, 'iri_base_3': 6.303749999999999, 'iri_base_5': 6.622877343749998, 'iri_base_8': 7.132114522009274, 'iri_projection_1': 6, 'iri_projection_10': 3.863345117187498, 'iri_projection_3': 6.303749999999999, 'iri_projection_5': 6.622877343749998, 'iri_projection_8': 3.677187499999999, 'length': 55.7246586607537, 'link_class': '5', 'management': '2', 'name': 'Bắc Quang-Xín Mần', 'npv': 10.045667331462528, 'npv_cost': 0.1704711924937048, 'npv_km': 0.1802732860620928, 'orma_way_id_x': '614835_302', 'orma_way_id_y': '614835_302', 'province': 'Hà Giang', 'road end location': 'thị trấn Cốc Pài, huyện Xín Mần', 'road number': 'ĐT.177', 'road start location': ' Km245, QL.2 (thị trấn Tân Quang, huyện Bắc Quang)', 'road_length': 55.7246586607537, 'roughness': 6, 'section_articulated_truck': None, 'section_commune_gso': None, 'section_delivery_vehicle': None, 'section_four_wheel': None, '

things_to_show = [
    ("ORMA ID", "orma_way_id_x"),
    ("Name", "name"),
    ("District", "district"),
    ("Surface", "surface"),
    ("Work Name", "work_name"),
    ("Work Class", "work_class"),
    ("Work Year", "work_year"),
    ("Work Cost", "work_cost"),
]

lu = {1: "#005AB588", 0: "#DC322088"}


def color_by_cba_ready(feature):
    ready = 1  # feature['properties']['cba_ready']
    return {"color": lu[ready], "weight": 1.4 + ready}


def color_by_year(feature):
    year = int(feature["properties"]["work_year"])
    return {"color": "#005AB5", "opacity": 0.9 - year * 0.03, "weight": 1.0 + (10 - year) * 0.1}


def get_year_color(year, color="#005AB5"):
    alpha = int((0.9 - year * 0.03) * 255)
    return f"{color}{alpha:2x}"


year_legend = {f"Year {y}": get_year_color(y) for y in [1, 3, 5, 8, 10]}

district_colors = [
    "#f77189",
    "#dc8932",
    "#ae9d31",
    "#77ab31",
    "#33b07a",
    "#36ada4",
    "#38a9c5",
    "#6e9bf4",
    "#cc7af4",
    "#f565cc",
]


def color_by_district(feature):
    district = feature["properties"]["district"]
    ix = int(hashlib.sha1(district.encode("utf-8")).hexdigest(), 16) % 10
    return {"color": district_colors[ix], "weight": 2.0, "opacity": 0.8}


district_legend = {}


def color_by_range(value, lu):
    c = None
    for c in lu[value]:
        break
    return {"color": c.data, "opacity": 1.0, "weight": 2.0}


npv_cost_colors, npv_cost_legend = IntervalTree(), {}
ranges = [(0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5), (0.5, 11.8)]
for c, (l, u) in zip(list(sns.color_palette("flare", 7).as_hex()), ranges):
    npv_cost_colors[l:u] = c
    npv_cost_legend[f"{l}-{u}"] = c


def color_by_npv_cost(feature):
    return color_by_range(feature["properties"]["npv_cost"], npv_cost_colors)


iri_colors, iri_legend = IntervalTree(), {}
ranges = [(0, 2.5), (2.5, 4.0), (4.0, 6.0), (6.0, 10.0), (10.0, 150.0)]
for c, (l, u) in zip(list(sns.color_palette("flare", 5).as_hex()), ranges):
    iri_colors[l:u] = c
    iri_legend[f"{l}-{u}"] = c


def color_by_iri(feature):
    return color_by_range(feature["properties"]["iri_base_1"], iri_colors)


def add_roads(m, df, attr):
    df.to_file("temp.json", driver="GeoJSON", encoding="utf-8")
    geojson_data = json.load(open("temp.json", "r"))

    map_geo = GeoJSON(
        data=geojson_data,
        style={"fillOpacity": 0.1},
        hover_style={"color": "red", "dashArray": "0", "fillOpacity": 0.5},
        style_callback=color_by_year,
    )
    layer = m.add_layer(map_geo)
    for d in df.district.unique():
        ix = int(hashlib.sha1(d.encode("utf-8")).hexdigest(), 16) % 10
        district_legend[d] = district_colors[ix]

    def update_attributes(feature, **kwargs):

        # print(feature['properties'].keys())
        inner_str = "\n".join([create_li(desc, feature["properties"][key]) for desc, key in things_to_show])
        attr.value = f"<ul class=attributes>{inner_str}</ul>"  #  + str(feature['properties'].keys())

    map_geo.on_hover(update_attributes)

    display(HTML("<style>.attributes { list-style-type: none; padding: 0; margin: 0; }</style>"))
    display(HTML("<style>.attributes .label { color: #AAAAAA; }</style>"))
    display(HTML("<style>.attributes .value { color: #000000; text-align: right }</style>"))
    return map_geo


def add_budget(m, gdf):
    total_budget = sum(gdf["work_cost"])
    budget_callout = HTML(
        f"""
        <div class='budget_label'>Total Budget ($USD)</div>
        <div class='budget_total'>${total_budget:.2f}M </div>
    """
    )
    budget_callout.layout.margin = "5px 10px 5px 10px"
    budget_control = WidgetControl(widget=budget_callout, position="bottomleft")

    m.clear_controls()
    m.add_control(budget_control)
    display(HTML("<style>.budget_label { font-size: 8pt; color: #BBB; }</style>"))
    display(HTML("<style>.budget_total { font-size: 20pt; width: 100%; text-align: center}</style>"))
