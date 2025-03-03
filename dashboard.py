import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


# Title of the dashboard
st.title("Yahoo Cryptocurrency Real-Time Dashboard")

# Fetch real-time data with user-defined dates
cryptos = ['BTC-USD', 'ETH-USD', 'LTC-USD']
start_date = st.date_input("Start date", value=pd.to_datetime("2022-01-01"))
end_date = st.date_input("End date", value=pd.to_datetime("today"))

import time

# Fetch real-time data with error handling
def fetch_data():
    while True:
        try:
            data = yf.download(cryptos, start=start_date, end=end_date, interval='1m')

            return data
        except Exception as e:
            st.error("No data fetched. Please check the date range.")

        except yf.YFRateLimitError:
            st.warning("Rate limit exceeded. Retrying in 60 seconds...")
            time.sleep(60)

data = fetch_data()


# Display the data
st.subheader("Real-Time Data")
st.write(data)

# Plotting the closing prices using Plotly
for crypto in cryptos:
    fig = px.line(data, x=data.index, y=data[crypto]['Close'], title=f"{crypto} Closing Prices")

    fig.update_layout(xaxis_title="Time", yaxis_title="Price (USD)")
    st.plotly_chart(fig)


# Additional visualizations can be added here
