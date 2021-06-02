import streamlit as st
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


df = pd.read_csv('notebooks/streamer_df_25pages')
st.write(df.head)


st.button("Re-run")

pts = 50
x1 = np.arange(pts)
y1 = np.random.random(pts)
y2 = np.random.random(pts)
y3 = (x1/pts)**2

fig = make_subplots(rows=1, cols=2)

fig.add_trace(go.Scatter(x=x1,y=y1,
                    mode='markers',
                    name='markers'),row=1,col=1)
fig.add_trace(go.Scatter(x=x1,y=y2,
                    mode='markers',
                    name='markers2'),row=1,col=2)
fig.add_trace(go.Scatter(x=x1,y=y3,
                    mode='lines',
                    name='lines'),row=1,col=2)

fig.update_layout(height=300, width=800, title_text="Side By Side Subplots")

g = st.plotly_chart(fig)
