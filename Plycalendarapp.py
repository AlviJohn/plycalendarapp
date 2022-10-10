#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import numpy as np
import pandas as pd
from chart_studio import plotly as py
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from itertools import product
from datetime import datetime
import time
from PIL import Image

######Setting the Basics for the Page
st.set_page_config(page_title="PlyCalendarApp", page_icon="muscleman.jpg", layout="wide", initial_sidebar_state="auto")
st.title('Ply Calendar Dashboard')


# In[3]:


##############################Reading the Data and basic Processing of datetime
#@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def read_input():
    ##Reading Tyre Data and Ply Master
    tyre_data = pd.read_excel(open('QXi_Ply data from 1809.xlsx', 'rb'),sheet_name='Data') 
    ply_master = pd.read_excel(open('QXi_Ply data from 1809.xlsx', 'rb'),sheet_name='Ply Master') 
    Calendar_data= pd.read_csv('Calendar_data.csv')
    Calendar_data=pd.melt(Calendar_data, id_vars=['Calendar','Length Start', 'Length End'], 
             var_name='Width', value_name='Gauge')
    tyre_data =tyre_data[['BARCODE','RFPP CW','GT Date', 'Rejection Param','Calendar','Cassette']]
    ply_master =ply_master[['Area Produced', 'Material Code', 'Material ID', 'Carrier ID', 'Shift','DOM ', 'Quantity', 'UOM', 'Material Status', 'Calander Referance','Trial', 'Source']] 
    return tyre_data,ply_master,Calendar_data


# In[ ]:


###########################################Selections#########################################
st.sidebar.title('Dashboard Filters')
st.sidebar.text('Apply Filters')


# In[ ]:


tyre_data,ply_master,gauge_master = read_input()


# In[ ]:


###Selecting Date for aggregation
start_date = tyre_data['GT Date'].min()
end_date = tyre_data['GT Date'].max()
    
#######Date Selection for calendar
col1, col2 = st.sidebar.columns(2)
with col1:
    starting_date = st.sidebar.date_input('Starting GT date', start_date)
with col2:
    ending_date = st.sidebar.date_input('Ending GT date', end_date)
if starting_date > ending_date:
        st.error('Error: End date must fall after start date.')
tyre_data_filtered = tyre_data[(tyre_data['GT Date'] >= start_date) & (tyre_data['GT Date'] <= end_date)]


####Selecting the calendar
calendar_choices = tyre_data_filtered['Calendar'].unique().tolist()
calendar_choices_V2 =calendar_choices
calendar_choices_V2.insert(0,"ALL")
calendar_make_choice = st.sidebar.multiselect("Select one or more Calendar:",calendar_choices_V2,'ALL')
if "ALL" in calendar_make_choice:
    calendar_make_choice_final = calendar_choices
else:
    calendar_make_choice_final = calendar_make_choice


###Filtering for specific Casette    
gauge_subset = gauge_master[gauge_master['Calendar'].isin(calendar_make_choice_final)]
tyre_subset = tyre_data_filtered[tyre_data_filtered['Calendar'].isin(calendar_make_choice_final)]
tyre_subset=tyre_subset.sort_values(by='Cassette',ascending=False, axis=0)


image = Image.open('muscle_man2.png')
st.sidebar.image(image)


# In[ ]:


#calendar_Reference ='L250922850110144'
#tyre_subset = tyre_data[tyre_data['Calendar']==calendar_Reference]
#tyre_subset=tyre_subset.sort_values(by='Cassette',ascending=False, axis=0)
#gauge_subset = Calendar_data[Calendar_data['Calendar']==calendar_Reference]


# In[ ]:


###RFPP for Cassette & Calendar
fig = px.histogram(tyre_subset, x="RFPP CW", title='Distribution of RFPP for Calendar')
st.plotly_chart(fig,use_container_width=True)

st.write(tyre_subset["RFPP CW"].describe().T)



# In[ ]:


fig = px.histogram(gauge_subset, x="Gauge",title="Distribution of Gauge")
st.plotly_chart(fig,use_container_width=True)


# In[ ]:


def df_to_plotly(df):
    return {'z': gauge_subset.Gauge.tolist(),
            'x': gauge_subset.Width.tolist(),
            'y': gauge_subset['Length Start'].tolist()}

import plotly.graph_objects as go
fig = go.Figure(data=go.Heatmap(df_to_plotly(gauge_subset)),)
fig.update_layout(
    title='Ply Gauge Measurement Across Length',
    xaxis_title="Width",
    yaxis_title="Length",
    legend_title="Gauge Measurement",
    font=dict(
        family="Courier New, monospace",
        size=13
    )
)

st.plotly_chart(fig,use_container_width=True)

#print(tyre_subset["RFPP CW"].describe())

#st.write(calendar_make_choice[0])
if (calendar_make_choice[0] != 'ALL'):
    fig = px.histogram(tyre_subset, x="RFPP CW",facet_col = 'Cassette', title='Distribution of RFPP for Cassettes')
    st.plotly_chart(fig,use_container_width=True)
    st.write(tyre_subset.groupby('Cassette')['RFPP CW'].describe())


