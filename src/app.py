from random import choice
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from src.dirs import DATAHOME
from src.io import load_jsonls


def load_data_into_regions():
    regions = DATAHOME / 'processed' / 'demand'
    regions = [e.name for e in regions.iterdir() if e.is_dir()]
    return {
        region: pd.read_csv(DATAHOME / 'processed' / 'demand' / region / 'all.csv')
        for region in regions
    }

def plot_all_regions_time_series(data):
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['SETTLEMENTDATE'], empty='none')

    data = data.reset_index().melt('SETTLEMENTDATE')

    line = alt.Chart(data).mark_line().encode(
        alt.X('SETTLEMENTDATE:T'),#axis=alt.Axis(values=data.index[::sep].values)),
        alt.Y('value:Q'),
        color='variable:N'
    )
    selectors = alt.Chart(data).mark_point().encode(
        x='SETTLEMENTDATE',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )
    text = line.mark_text(align='left', dx=0, dy=-10).encode(
        text=alt.condition(nearest, 'value:Q', alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(data).mark_rule(color='gray').encode(
        x='SETTLEMENTDATE',
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    lyr = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=600, height=300, title=str(data.loc[:, 'SETTLEMENTDATE'].iloc[0])
    )

    return st.altair_chart(lyr, use_container_width=True)


def combine_all_regions(regions):
    cols, data = [], []
    for r, d in regions.items():
        cols.append(r)
        sub = d.loc[:, ['TOTALDEMAND', 'SETTLEMENTDATE']]
        sub = sub.set_index('SETTLEMENTDATE', drop=True)
        data.append(sub)
    data = pd.concat(data, axis=1)
    data.columns = cols
    return data.sort_index()


if __name__ == '__main__':
    regions = load_data_into_regions()

    all_region_demand = combine_all_regions(regions)

    st.title('Similar Day Foreceasting with Variational Auto-Encoders')

    st.header('EDA of All Regions')
    st.text(f'{all_region_demand.index[0]} to {all_region_demand.index[-1]}')
    st.text('Random sample of demand for each region:')
    st.write(all_region_demand.sample())

    st.text('Summary statistics of demand for each region:')
    st.write(all_region_demand.describe().loc[['mean', 'std', 'min', 'max'], :])

    start_date = st.selectbox(
        'Start date:',
        list(all_region_demand.index)[::7*288]
    )

    plot_all_regions_time_series(
        all_region_demand.loc[start_date:, :].iloc[:7*288, :]
    )

    st.header('Yesterday Baseline')
    region = st.selectbox(
        'Region:',
        list(regions.keys())
    )
    region = 'SA1'

    path = DATAHOME / 'final' / 'baselines' / 'yesterday' / region
    days = [p.name for p in path.iterdir()]
    baselines = {
        day: pd.read_csv(path / day, index_col=0)
        for day in days
    }

    day = st.selectbox(
        'Select baseline day:',
        sorted(list(baselines.keys()))
    )

    data = baselines[day]
    data = data.set_index('target_index')
    baseline = data.loc[:, ['pred', 'target']].reset_index().melt('target_index')
    chart = alt.Chart(baseline).mark_line().encode(
        alt.X('target_index:T'),
        alt.Y('value:Q'),
        color='variable:N'
    )
    st.altair_chart(chart.properties(width=600, height=400))

    st.header('Both Baseline Error Analysis')
    error_chart = []
    for name in ['yesterday', 'week']:
        errors = DATAHOME / 'final' / 'baselines' / name / 'errors.csv'
        errors = pd.read_csv(errors)
        errors = errors.query('statistic == "mean"').query('variable == "abs-errors"').sort_values('target_day')
        errors = errors.drop(['statistic', 'variable'], axis=1)
        errors.columns = [name, errors.columns[1]]
        errors = errors.set_index(errors.columns[1])
        error_chart.append(errors)

    st.subheader('Groupby Weekday')
    for errors in error_chart:
        errors.index = pd.to_datetime(errors.index)
        errors = errors.groupby(errors.index.dayofweek).mean()
        st.text(errors.columns[0])
        st.text(f"MAE - {np.mean(errors).values[0]:.2f}")
        st.bar_chart(errors)

    st.subheader('Groupby Month')
    for errors in error_chart:
        errors.index = pd.to_datetime(errors.index)
        errors.index.name = 'dt'
        errors = errors.groupby([errors.index.month]).mean()
        st.text(errors.columns[0])
        st.text(f"MAE - {np.mean(errors).values[0]:.2f}")
        st.bar_chart(errors)

    st.subheader('Groupby Month & Year')
    for errors in error_chart:
        errors.index = pd.to_datetime(errors.index)
        errors.index.name = 'dt'
        errors = errors.groupby([errors.index.year, errors.index.month]).mean()
        st.text(errors.columns[0])
        st.text(f"MAE - {np.mean(errors).values[0]:.2f}")
        errors.index = pd.to_datetime([f'{y}-{d}' for y, d in errors.index])
        st.bar_chart(errors)
