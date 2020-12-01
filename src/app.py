from random import choice
import streamlit as st
import pandas as pd
import altair as alt
from src.dirs import DATAHOME
from src.io import load_jsonls


st.title('Similar Day Foreceasting with Variational Auto-Encoders')

regions = DATAHOME / 'processed' / 'demand'
regions = [e.name for e in regions.iterdir() if e.is_dir()]

regions = {
    region: pd.read_csv(DATAHOME / 'processed' / 'demand' / region / 'all.csv')
    for region in regions
}
region = st.selectbox('Select region:', list(regions.keys()) + ['ALL'])
region = 'ALL'
if region != 'ALL':
    print(f'You selected: {region}')
    data = regions[region]
    data = data.set_index('SETTLEMENTDATE').sort_index()

elif region == 'ALL':
    cols, data = [], []
    for r, d in regions.items():
        cols.append(r)
        sub = d.loc[:, ['TOTALDEMAND', 'SETTLEMENTDATE']]
        sub = sub.set_index('SETTLEMENTDATE', drop=True)
        data.append(sub)
    data = pd.concat(data, axis=1)
    data.columns = cols
else:
    assert 1 == 0

data = data.iloc[:7*268, :]
print(data.head())

# if st.checkbox('Show dataframe'):
st.write(data.sample())
#  plot the below
st.write(data.describe().loc[['mean', 'std', 'min', 'max'], :])

if data.shape[0] > 286:
    sep = 286
else:
    sep = 12

# The basic line
# if st.checkbox('Show chart'):
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
    width=600, height=300
)

st.altair_chart(lyr, use_container_width=True)

region = 'SA1'
path = DATAHOME / 'final' / 'baselines' / 'yesterday' / region
days = [p.name for p in path.iterdir()]
baselines = {
    day: pd.read_csv(path / day, index_col=0)
    for day in days
}
print(baselines.keys())
day = choice(list(baselines.keys()))
print(day)
data = baselines[day]
data = data.set_index('target_index')
st.line_chart(data.loc[:, ['pred', 'target']])

baseline = data.loc[:, ['pred', 'target']].reset_index().melt('target_index')
chart = alt.Chart(baseline).mark_line().encode(
    alt.X('target_index:T'),
    alt.Y('value:Q'),
    color='variable:N'
)
st.altair_chart(chart.properties(width=600, height=400))
name = 'week'
error_chart = []
for name in ['yesterday', 'week']:
    errors = DATAHOME / 'final' / 'baselines' / name / 'errors.csv'
    errors = pd.read_csv(errors)

    st.line_chart(data.loc[:, 'errors'])

    errors = errors.query('statistic == "mean"').query('variable == "errors"').sort_values('target_day')
    errors = errors.drop(['statistic', 'variable'], axis=1)
    errors.columns = [name, errors.columns[1]]
    errors = errors.set_index(errors.columns[1])
    error_chart.append(errors)

errors = pd.concat(error_chart, axis=1)
for errors in error_chart:
    errors.index = pd.to_datetime(errors.index)
    errors = errors.dropna(axis=0)
    errors = errors.groupby(errors.index.dayofweek).mean()
    st.bar_chart(
        errors
    )
