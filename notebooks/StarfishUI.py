import streamlit as st
import numpy as np
import pandas as pd
import time
#from notebooks.twitchtracker_games_function_done import parse_games_2

df = pd.read_csv('streamer_df_clean')
st.write(df["Hours Watched"].)

with st.form(key='my_form'):
    text_input = st.text_input(label='Enter your name')
    submit_button = st.form_submit_button(label='Submit')



#shroud_df = parse_games_2("Shroud")
#shroud_df.plot()


def cool_chart():
  progress_bar = st.progress(0)
  status_text = st.empty()
  chart = st.line_chart(np.random.randn(10, 2))

  for i in range(100):
      # Update progress bar.
      progress_bar.progress(i + 1)

      new_rows = np.random.randn(10, 2)

      # Update status text.
      status_text.text(
          'The latest random number is: %s' % new_rows[-1, 1])

      # Append data to the chart.
      chart.add_rows(new_rows)

      # Pretend we're doing some computation that takes time.
      time.sleep(0.1)

  status_text.text('Done!')
  st.balloons()

#cool_chart()

# Get some data.
data = np.random.randn(10, 2)

# Show the data as a chart.
chart = st.line_chart(data)

# Wait 1 second, so the change is clearer.
time.sleep(1)

# Grab some more data.
data2 = np.random.randn(10, 2)

# Append the new data to the existing chart.
chart.add_rows(data2)





#sidebar
#for i in range(int(st.number_input('Num:'))): foo()
#if st.sidebar.selectbox('I:',['ffff']) == 'f': b()
#my_slider_val = st.slider('Quinn Mallory', 1, 88)
#st.write(slider_val)