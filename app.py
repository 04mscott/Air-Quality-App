import pandas as pd
import streamlit as st
import plotly.express as px
from prediction import predict_n
from location_data import get_current_air_quality



st.html("<h1 style='text-align: center; color: white;'>Air Quality Predictor</h1>")
# st.title('Air Quality Predictor')

city = st.text_input('Enter a City to Get Curret Air Quality')

if city:
    pollutants = ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']
    pollutants_cb = ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']
    colors = ['#eb4034', '#e68439', '#e8c433', '#a6e32b', '#14e07a', '#1bc3e0', '#2154de', '#a827db']

    df_current = get_current_air_quality(city, 72)
    # if df_current is not None:
    df = predict_n(df_current, 24)
    # if df is not None:
    # df = df.iloc[-49:]
    a, b, c, d, e, f, g, h = st.columns(8)
    columns = [a, b, c, d, e, f, g, h]

    co = a.checkbox('co', value=True, key=None, help=None, on_change=None, args=None, kwargs=None,disabled=False, label_visibility="visible")
    no = b.checkbox('no', value=True, key=None, help=None, on_change=None, args=None, kwargs=None,disabled=False, label_visibility="visible")
    no2 = c.checkbox('no2', value=True, key=None, help=None, on_change=None, args=None, kwargs=None,disabled=False, label_visibility="visible")
    o3 = d.checkbox('o3', value=True, key=None, help=None, on_change=None, args=None, kwargs=None,disabled=False, label_visibility="visible")
    so2 = e.checkbox('so2', value=True, key=None, help=None, on_change=None, args=None, kwargs=None,disabled=False, label_visibility="visible")
    pm2_5 = f.checkbox('pm2_5', value=True, key=None, help=None, on_change=None, args=None, kwargs=None,disabled=False, label_visibility="visible")
    pm10 = g.checkbox('pm10', value=True, key=None, help=None, on_change=None, args=None, kwargs=None,disabled=False, label_visibility="visible")
    nh3 = h.checkbox('nh3', value=True, key=None, help=None, on_change=None, args=None, kwargs=None,disabled=False, label_visibility="visible")
    
    if co:
        if 'co' not in pollutants_cb and '#eb4034' not in colors:
            pollutants_cb.append('co')
            colors.append('#eb4034')
    else:
        pollutants_cb.remove('co')
        colors.remove('#eb4034')
    if no:
        if 'no' not in pollutants_cb and '#e68439' not in colors:
            pollutants_cb.append('no')
            colors.append('#e68439')
    else:
        pollutants_cb.remove('no')
        colors.remove('#e68439')
    if no2:
        if 'no2' not in pollutants_cb and '#e8c433' not in colors:
            pollutants_cb.append('no2')
            colors.append('#e8c433')
    else:
        pollutants_cb.remove('no2')
        colors.remove('#e8c433')
    if o3:
        if 'o3' not in pollutants_cb and '#a6e32b' not in colors:
            pollutants_cb.append('o3')
            colors.append('#a6e32b')
    else:
        pollutants_cb.remove('o3')
        colors.remove('#a6e32b')
    if so2:
        if 'so2' not in pollutants_cb and '#14e07a' not in colors:
            pollutants_cb.append('so2')
            colors.append('#14e07a')
    else:
        pollutants_cb.remove('so2')
        colors.remove('#14e07a')
    if pm2_5:
        if 'pm2_5' not in pollutants_cb and '#1bc3e0' not in colors:
            pollutants_cb.append('pm2_5')
            colors.append('#1bc3e0')
    else:
        pollutants_cb.remove('pm2_5')
        colors.remove('#1bc3e0')
    if pm10:
        if 'pm10' not in pollutants_cb and '#2154de' not in colors:
            pollutants_cb.append('pm10')
            colors.append('#2154de')
    else:
        pollutants_cb.remove('pm10')
        colors.remove('#2154de')
    if nh3:
        if 'nh3' not in pollutants_cb and '#a827db' not in colors:
            pollutants_cb.append('nh3')
            colors.append('#a827db')
    else:
        pollutants_cb.remove('nh3')
        colors.remove('#a827db')

    df['time'] = pd.to_datetime(df['time'], unit='s')
    vertical_line_time = df['time'].iloc[-25]

    fig = px.line(
        df,
        x="time", 
        y=pollutants_cb, 
        range_x=[df['time'].min(), df['time'].max()], 
        labels={'time': 'Time', 'value': 'Concentration μg/m3'}
    )
    fig.add_vline(x=vertical_line_time, line_width=3, line_dash="dash", line_color="red")
    fig.add_vrect(x0=vertical_line_time, x1=df['time'].max(), line_width=0, fillcolor="gray", opacity=0.2)
    # fig.show()

    st.plotly_chart(fig)

    st.sidebar.text('Pollutant Concentrations (μg/m3)')
    # st.text('Current Concentrations (μg/m3)')

    for i, p in enumerate(pollutants):
        last_real_value = float(df[p].iloc[-25])
        previous_value = float(df[p].iloc[-26])
        #column = a1 if i < 4 else c1
        st.sidebar.metric(
            p, 
            round(last_real_value, 2), 
            delta=round(previous_value-last_real_value, 2), 
            delta_color="inverse", 
            help=None, 
            label_visibility="visible", 
            border=False
        )