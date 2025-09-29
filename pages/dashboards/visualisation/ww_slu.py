import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from django.utils.text import slugify
from datetime import datetime, timedelta
from plotly.subplots import make_subplots

# Color settings

cities_graph_info = {
    "Gavle": {"colour": "#d6604d", "symbol": "hourglass"},
    "Goteborg": {"colour": "#9400d3", "symbol": "cross"},
    "Helsingborg": {"colour": "#efb261", "symbol": "square"},
    "Jonkoping": {"colour": "#ffa500", "symbol": "cross"},
    "Kalmar": {"colour": "#f4a582", "symbol": "hourglass"},
    "Karlstad": {"colour": "#67001f", "symbol": "square"},
    "Linkoping": {"colour": "#b2182b", "symbol": "cross"},
    "Lulea": {"colour": "#2166ac", "symbol": "cross"},
    "Malmo": {"colour": "#4393c3", "symbol": "square"},
    "Orebro": {"colour": "#b8860b", "symbol": "square"},
    "Ostersund": {"colour": "#997950", "symbol": "hourglass"},
    "Osthammar": {"colour": "#778899", "symbol": "hourglass"},
    "Stockholm-Bromma": {"colour": "#000000", "symbol": "cross"},
    "Stockholm-Grodinge": {"colour": "#ff00ff", "symbol": "square"},
    "Stockholm-Henriksdal": {"colour": "#4adede", "symbol": "cross"},
    "Stockholm-Kappala": {"colour": "#ffd700", "symbol": "square"},
    "Umea": {"colour": "#053061", "symbol": "hourglass"},
    "Uppsala": {"colour": "#663399", "symbol": "square"},
    "Vasteras": {"colour": "#b691d2", "symbol": "hourglass"},
}

yearcolors_map = {"2024": "#4393c3", "2025": "#9400d3"}

hmapcolors_map = {
    "Invalid sample": "#d6604d",
    "Negative sample": "#b691d2",
    "Positive sample": "#2166ac",
}
hmapcolors = list(hmapcolors_map.values())

bgcolor = "#ffffff"
gridcolor = "#e8e8e8"
linecolor = "#d6d6d6"

# Common dicts and lists used by multiple function

plotly_to_html_settings = dict(
    include_plotlyjs="cdn", full_html=False, config=dict(displayModeBar=False)
)

norm_methods_map = {
    "pmmov_normalised": "PMMoV",
    "copies_day_inhabitant": "Wastewater flow",
    "copies_l": "None (copies/litre)",
}

timeseries_map = {
    1: "Weekly",
    2: "Rolling average, 2 weeks",
    3: "Rolling average, 3 weeks",
    4: "Rolling average, 4 weeks",
}

common_axes_settings = dict(
    title="",
    linewidth=0.8,
    linecolor=linecolor,
    mirror=True,
    zerolinecolor=bgcolor,
    fixedrange=True,
)

scatter_axes_settings = dict(
    matches=None,
    showgrid=True,
    gridcolor=gridcolor,
    gridwidth=0.8,
    **common_axes_settings,
)

base_legend = dict(
    title="",
    itemsizing="constant",
    borderwidth=0.8,
    bordercolor=linecolor,
)

horizontal_legend = dict(
    orientation="h", x=0.5, xanchor="center", yanchor="bottom", **base_legend
)

zero_margin = dict(
    t=0,
    r=10,
    b=0,
    l=0,
)


def get_compiled_data(data_url):
    compiled_data = {}
    data = read_data(data_url)

    # store raw data to be used by plots with filters
    compiled_data["raw_data"] = data.replace(np.nan, None).to_dict()

    # site info for methodology page
    compiled_data["sites_info"] = get_sites_info(data=data)

    # required info for filter inputs
    compiled_data["filter_input_context"] = get_filter_input_context(data=data)

    # recent data info for overview page
    compiled_data["recent_data_info"] = get_recent_data_info(data=data)

    # qualitative combined plot
    compiled_data["qual_overview_plot"] = get_qual_overview_plot(data=data)

    # qualitavtive plot for each virus
    for virus in data.target.unique().tolist():
        compiled_data[f"qual_plot_{slugify(virus)}"] = get_qual_plots(
            data=data, virus=virus
        )

    return compiled_data


def read_data(data_url):
    return pd.read_csv(data_url, sep=",")


def get_range_date(all_dates, year, format="%Y-%m-%d"):
    all_dates = all_dates[all_dates.str.contains(year)]
    min_date = datetime.strptime(all_dates.min(), format) - timedelta(days=3)
    max_date = datetime.strptime(all_dates.max(), format) + timedelta(days=3)
    return [min_date.strftime(format), max_date.strftime(format)]


def get_timeline_annotation_updatemenus(
    timeline, years, x=0.53, y=-0.2, resize_yaxis=False, ydata=None
):
    annotations = [
        dict(
            text="Select Timeline:",
            showarrow=False,
            borderpad=5,
            x=x,
            y=y + 0.02,
            xshift=-135,
            xanchor="center",
            yanchor="bottom",
            xref="paper",
            yref="paper",
            font=dict(size=12),
        )
    ]

    updatemenus = [
        dict(
            type="buttons",
            direction="left",
            active=len(years),
            x=x,
            xanchor="center",
            y=y,
            yanchor="bottom",
            pad=dict(b=5),
            buttons=[
                dict(label="All", method="relayout", args=[{"xaxis.autorange": True}]),
            ],
        )
    ]

    if resize_yaxis:
        updatemenus[0]["buttons"][0]["args"][0]["yaxis.autorange"] = True

    for y in years:
        button = dict(
            label=y,
            method="relayout",
            args=[{"xaxis.range": get_range_date(timeline, str(y))}],
        )
        if resize_yaxis and ydata is not None:
            ymax = max(ydata[timeline.str.contains(str(y))])
            button["args"][0]["yaxis.range"] = [round(ymax * -0.07, 2), ymax * 1.2]
        updatemenus[0]["buttons"].append(button)

    return (annotations, updatemenus)


def get_sites_info(data):
    data = data[["city", "inhabitants"]].drop_duplicates().sort_values("city")
    city_info = [["Site", "Num. of residents"]]
    return city_info + data.to_dict("tight")["data"]


def get_filter_input_context(data):
    data_sampling_date = pd.to_datetime(data.sampling_date)

    return {
        "input_years": data_sampling_date.apply(lambda d: d.year).unique().tolist(),
        "input_months": data_sampling_date.apply(lambda d: d.month).unique().tolist(),
        "input_viruses": sorted(data.target.unique().tolist()),
        "input_sites": sorted(data.city.unique().tolist()),
        "input_methods": norm_methods_map,
        "input_timeseries": timeseries_map,
    }


def get_recent_data_info(data):
    sampling_date = max(data.sampling_date)

    recent_data = data[data.sampling_date == sampling_date]
    recent_data_pop = recent_data[["city", "inhabitants"]].drop_duplicates()
    recent_data_cities = recent_data_pop.city.tolist()

    sampling_sites = (
        f"{', '.join(recent_data_cities[:-1])} and {recent_data_cities[-1]}."
    )
    sampling_sites_pop = round((recent_data_pop.inhabitants.sum() / 10587710) * 100)

    sample_summary = [["Target", "Analysed", "Positive", "Valid"]]
    for name, group in recent_data.groupby("target"):
        sample_summary.append(
            [
                name,
                int(group.category.count()),
                sum(group.category == "Positive sample"),
                sum(group.category != "Invalid sample"),
            ]
        )

    return {
        "sampling_date": sampling_date,
        "sampling_sites": sampling_sites,
        "sampling_sites_pop": sampling_sites_pop,
        "sample_summary": sample_summary,
    }


def get_quant_overview_plot(data, **f_args):
    # check if data is a dict, if so conver it to dataframe
    if isinstance(data, dict):
        data = pd.DataFrame.from_records(data)

    # get passed filter args, if not passed use defaults
    f_year = (
        list(map(int, f_args.get("year", [])))
        or pd.to_datetime(data.sampling_date).apply(lambda d: d.year).unique().tolist()
    )
    f_month = [1, int(f_args.get("months", ["12"])[0])]
    f_sites = f_args.get("site", data.city.unique().tolist())
    f_method = f_args.get("method", ["pmmov_normalised"])[0]
    f_roll = int(f_args.get("timeseries", ["3"])[0])

    cols_common = ["target", "sampling_date", "week", "month", "year"]
    cols_values = ["pmmov_normalised", "copies_day_inhabitant", "copies_l"]
    cols_todrop = ["sample", "city", "category"] + cols_values

    data = data.join(
        pd.DataFrame(
            [
                [[d.week, 53][d.week == 1 and d.month == 12], d.month, d.year]
                for d in pd.to_datetime(data.sampling_date)
            ],
            columns=["week", "month", "year"],
            index=data.index,
        )
    )

    data_filtered = data[
        data.city.isin(f_sites)
        & data.year.isin(f_year)
        & (data.month >= f_month[0])
        & (data.month <= f_month[1])
    ].reset_index(drop=True)
    data_filtered["y_val"] = data_filtered[f_method]
    data_filtered.drop(cols_todrop, axis=1, inplace=True)

    data_processed = (
        data_filtered.groupby(cols_common)
        .apply(
            lambda d: (d.y_val * d.inhabitants).sum() / d.inhabitants.sum(),
            include_groups=False,
        )
        .rename("y_val")
        .reset_index()
    )
    # convert year column to string for legend mapping
    data_processed["year"] = data_processed.year.astype("str")

    fig = px.scatter(
        data_processed,
        x="week",
        y="y_val",
        color="year",
        trendline="rolling",
        trendline_options=dict(function="mean", window=f_roll, min_periods=1),
        facet_col="target",
        facet_col_wrap=2,
        facet_col_spacing=0.05,
        facet_row_spacing=0.15,
        color_discrete_map=yearcolors_map,
    )

    fig.update_xaxes(showticklabels=True, **scatter_axes_settings)
    fig.update_yaxes(showticklabels=True, **scatter_axes_settings)

    fig.update_layout(
        plot_bgcolor=bgcolor,
        hovermode=False,
        title=dict(
            text="Week",
            x=0.51,
            y=0.1,
            xanchor="center",
            yanchor="bottom",
            font=dict(size=16),
        ),
        legend=dict(y=-0.25, **horizontal_legend),
        margin=dict(t=18, r=20, b=0, l=0),
    )
    fig.for_each_annotation(
        lambda a: a.update(text=a.text.split("=")[-1], yshift=3, font={"size": 14})
    )

    return fig.to_html(**plotly_to_html_settings)


def get_qual_overview_plot(data):
    cols_togroup = ["sampling_date", "target", "category"]
    cols_todrop = [
        "sample",
        "inhabitants",
        "pmmov_normalised",
        "copies_day_inhabitant",
        "copies_l",
    ]
    data = data.drop(cols_todrop, axis=1).drop_duplicates().reset_index(drop=True)

    data_bar = data.groupby(cols_togroup).size().rename("category_count").reset_index()
    data_bar["category_percent"] = (
        data_bar["category_count"] * 100
    ) / data_bar.groupby(cols_togroup[:-1])["category_count"].transform("sum")
    data_bar = data_bar.sort_values(cols_togroup, ascending=[True, True, False])

    fig = px.bar(
        data_bar,
        x="sampling_date",
        y="category_percent",
        color="category",
        color_discrete_map=hmapcolors_map,
        facet_col="target",
        facet_col_wrap=2,
        facet_col_spacing=0.05,
        facet_row_spacing=0.15,
    )
    fig.update_traces(marker_line_width=0)

    fig.update_xaxes(matches=None, showticklabels=True, **common_axes_settings)

    fig.update_yaxes(
        matches=None, showticklabels=True, range=[0, 100], **common_axes_settings
    )

    fig.update_layout(
        plot_bgcolor=bgcolor,
        hovermode=False,
        barmode="stack",
        bargap=0,
        legend=dict(y=-0.2, **horizontal_legend),
        hoverlabel=dict(bgcolor=bgcolor),
        margin=dict(t=20, r=20, b=0, l=0),
    )
    fig.for_each_annotation(
        lambda a: a.update(text=a.text.split("=")[-1], yshift=3, font={"size": 14})
    )

    return fig.to_html(**plotly_to_html_settings)


def get_all_sites_plot(data, virus, **f_args):
    # check if data is a dict, if so conver it to dataframe
    if isinstance(data, dict):
        data = pd.DataFrame.from_records(data)

    # filter args processing and default
    f_method = f_args.get("method", ["pmmov_normalised"])[0]
    f_roll = int(f_args.get("timeseries", ["1"])[0])

    cols_tosort = ["city", "sampling_date"]
    cols_todrop = ["sample", "inhabitants", "category"]

    data = (
        data[data.target == virus]
        .drop(cols_todrop, axis=1)
        .sort_values(cols_tosort)
        .reset_index(drop=True)
    )

    plot_trace = []
    for city, group in data.groupby("city"):
        plot_trace.append(
            go.Scatter(
                name=city,
                x=group.sampling_date,
                y=group[f_method].rolling(f_roll, min_periods=1).mean(),
                mode="lines+markers",
                marker=dict(color=cities_graph_info[city]["colour"]),
                line=dict(color=cities_graph_info[city]["colour"]),
            )
        )

    fig = go.Figure(data=plot_trace)

    fig.update_xaxes(hoverformat="%b %d, %Y (week %V)", **common_axes_settings)
    fig.update_yaxes(
        showgrid=True, gridcolor=gridcolor, gridwidth=0.8, **common_axes_settings
    )

    years = pd.to_datetime(data.sampling_date).apply(lambda d: d.year).unique().tolist()
    fig.update_xaxes(range=get_range_date(data.sampling_date, str(years[-1])))
    ymax = max(data[f_method][data.sampling_date.str.contains(str(years[-1]))])
    fig.update_yaxes(range=[round(ymax * -0.07, 2), ymax * 1.2])

    annotations, updatemenus = get_timeline_annotation_updatemenus(
        data.sampling_date,
        years,
        x=0.55,
        y=-0.22,
        resize_yaxis=True,
        ydata=data[f_method],
    )

    fig.update_layout(
        plot_bgcolor=bgcolor,
        hovermode="x unified",
        hoverdistance=1,
        annotations=annotations,
        updatemenus=updatemenus,
        legend=dict(font=dict(size=10)),
        margin=zero_margin,
    )

    return fig.to_html(**plotly_to_html_settings)


def get_single_site_plot(data, virus, **f_args):
    # check if data is a dict, if so conver it to dataframe
    if isinstance(data, dict):
        data = pd.DataFrame.from_records(data)

    f_roll = int(f_args.get("timeseries", ["1"])[0])
    f_site = f_args.get("site", data.city.unique())[0]

    cols_todrop = ["target", "sample", "inhabitants", "category"]
    cols_values = ["pmmov_normalised", "copies_day_inhabitant", "copies_l"]
    methods_map = {
        "pmmov_normalised": {
            "name": "PMMoV normalised",
            "scale": 66983,
            "colour": "#4393c3",
        },
        "copies_day_inhabitant": {
            "name": "Flow normalised",
            "scale": 0.003,
            "colour": "#9400d3",
        },
        "copies_l": {"name": "Non normalised", "scale": 1, "colour": "#b691d2"},
    }

    data = (
        data[data.target == virus]
        .drop(cols_todrop, axis=1)
        .sort_values("sampling_date")
        .drop_duplicates()
        .reset_index(drop=True)
    )
    for col in cols_values:
        data[col] = data[col].rolling(f_roll).mean()
    data = data[data.city == f_site].drop_duplicates().reset_index(drop=True)

    plot_traces = []
    for i, vcol in enumerate(methods_map.keys()):
        plot_traces.append(
            go.Scatter(
                name=methods_map[vcol]["name"],
                x=data.sampling_date,
                y=data[vcol] * methods_map[vcol]["scale"],
                mode="lines+markers",
                marker=dict(color=methods_map[vcol]["colour"]),
                line=dict(color=methods_map[vcol]["colour"]),
            )
        )

    fig = go.Figure(data=plot_traces)

    fig.update_xaxes(**scatter_axes_settings)
    fig.update_yaxes(showticklabels=False, **scatter_axes_settings)

    years = pd.to_datetime(data.sampling_date).apply(lambda d: d.year).unique().tolist()
    fig.update_xaxes(range=get_range_date(data.sampling_date, str(years[-1])))

    annotations, updatemenus = get_timeline_annotation_updatemenus(
        data.sampling_date, years, x=0.53, y=-0.39
    )

    fig.update_layout(
        plot_bgcolor=bgcolor,
        annotations=annotations,
        updatemenus=updatemenus,
        hovermode=False,
        legend=dict(y=-0.22, **horizontal_legend),
        margin=zero_margin,
    )

    return fig.to_html(**plotly_to_html_settings)


def get_qual_plots(data, virus):
    cols_todrop = [
        "sample",
        "inhabitants",
        "pmmov_normalised",
        "copies_day_inhabitant",
        "copies_l",
    ]
    category_map = {
        "Invalid sample": "1",
        "Negative sample": "2",
        "Positive sample": "3",
    }

    data = (
        data[data.target == virus]
        .drop(cols_todrop, axis=1)
        .drop_duplicates()
        .reset_index(drop=True)
    )

    # data processing for heatmap
    pdata = data.pivot(index="city", columns="sampling_date", values="category")
    pdata_numeric = pdata.replace(category_map)
    pdata_text = pdata.fillna("Not Available")

    # data processing for stack bar
    data_bar = (
        data.groupby(["sampling_date", "category"])
        .size()
        .rename("category_count")
        .reset_index()
    )
    data_bar["category_percent"] = (
        data_bar["category_count"] * 100
    ) / data_bar.groupby("sampling_date")["category_count"].transform("sum")
    data_bar = data_bar.sort_values(
        ["sampling_date", "category"], ascending=[True, False]
    )

    # make subplots layout
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)

    fig.add_trace(
        go.Heatmap(
            z=pdata_numeric,
            x=pdata.columns,
            y=pdata.index,
            customdata=pdata_text,
            colorscale=hmapcolors,
            showscale=False,
            hovertemplate="Date: %{x}<br>City: %{y}<br>Type: %{customdata}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    bar_fig = px.bar(
        data_bar,
        x="sampling_date",
        y="category_percent",
        color="category",
        color_discrete_map=hmapcolors_map,
    )
    fig.add_traces(bar_fig["data"], rows=2, cols=1)
    fig.update_traces(marker_line_width=0, row=2)

    fig.update_xaxes(**common_axes_settings)
    fig.update_yaxes(**common_axes_settings)
    fig.update_yaxes(range=[0, 100], row=2, col=1)

    years = pd.to_datetime(data.sampling_date).apply(lambda d: d.year).unique().tolist()

    fig.update_xaxes(
        range=get_range_date(data.sampling_date, str(years[-1])), row=2, col=1
    )

    annotations, updatemenus = get_timeline_annotation_updatemenus(
        data.sampling_date, years, x=0.53, y=-0.2
    )

    fig.update_layout(
        plot_bgcolor=bgcolor,
        barmode="stack",
        bargap=0,
        annotations=annotations,
        updatemenus=updatemenus,
        legend=dict(**base_legend),
        hoverlabel=dict(bgcolor=bgcolor),
        margin=zero_margin,
    )

    return fig.to_html(**plotly_to_html_settings)
