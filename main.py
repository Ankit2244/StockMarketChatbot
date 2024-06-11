import json
import openai
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf

openai.api_key = open("API_KEY.txt").read()  # we read the API key from a text file
#create your own key and buy credits from the openai platform/sandbox to use the API


# Coding Financial Functions


def get_stock_price(ticker):
    return str(yf.Ticker(ticker).history(period="1y").iloc[-1].Close)
    # prompt will give the stock price of company


def calculate_SMA(ticker, window):
    data = yf.Ticker(ticker).history(period="1y").Close
    return data.rolling(window=window).mean().iloc[-1]


def calculate_EMA(ticker, window):
    data = yf.Ticker(ticker).history(period="1y").Close
    return data.rolling(span=window, adjust=False).mean().iloc[-1]


def calculate_RSI(ticker):
    data = yf.Ticker(ticker).history(period="1y").Close
    delta = data.diff()
    up = delta.clip(lower=0)
    lower = delta.clip(upper=0)
    ema_up = up.ewm(com=14 - 1, adjust=False).mean()
    ema_down = lower.ewm(com=14 - 1, adjust=False).mean()
    rs = ema_up / ema_down
    return str(100 - (100 / (1 + rs)).iloc[-1])


def calculate_MACD(ticker):
    data = yf.Ticker(ticker).history(period="1y").Close
    short_EMA = data.ewm(span=12, adjust=False).mean()
    long_EMA = data.ewm(span=26, adjust=False).mean()

    MACD = short_EMA - long_EMA
    signal = MACD.ewm(span=9, adjust=False).mean()
    MACD_histogram = MACD - signal
    return f'{MACD[-1]},{signal[-1], {MACD_histogram[-1]} }'


def plot_stock_price(ticker):
    data = yf.Ticker(ticker).history(period="1y").Close
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data.Close)
    plt.title(f'{ticker} Stock Price over last year')
    plt.xlabel('Date')
    plt.ylabel('Stock Price in USD')
    plt.grid()
    plt.savefig('stock.png')
    plt.close()


# To make GPT use functions we define them in a list containing dictionary ( A JSON FILE )

# Sq brackets for list and curly brackets for dictionary

functions = [
    {
        "name": "get_stock_price",
        "description": "Get the latest stock price of a company according to its given ticker symbol",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol of of a company (e.g. AAPL for Apple Inc.)"
                }
            },
            "required": ["ticker"]
        },
    },
    {
        "name": "calculate_SMA",
        "description": "Calculate the Simple Moving Average of a company's stock price",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol of of a company (e.g. AAPL for Apple Inc.)"
                },
                "window": {
                    "type": "integer",
                    "description": "The time frame to consider while calculating SMA"
                }
            },
            "required": ["ticker", "window"]
        },
    },
    {
        "name": "calculate_EMA",
        "description": "Calculate the Exponential Moving Average of a company's stock price",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol of of a company (e.g. AAPL for Apple Inc.)"
                },
                "window": {
                    "type": "integer",
                    "description": "The time frame to consider while calculating SMA"
                }
            },
            "required": ["ticker", "window"]
        },
    },
    {
        "name": "calculate_RSI",
        "description": "Calculate the Relative Strength Index of a company's stock price",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol of of a company (e.g. AAPL for Apple Inc.)"
                }
            },
            "required": ["ticker"]
        },
    },
    {
        "name": "calculate_MACD",
        "description": "Calculate the Moving Average Convergence Divergence of a company's stock price",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol of of a company (e.g. AAPL for Apple Inc.)"
                }
            },
            "required": ["ticker"]
        },
    },
    {
        "name": "plot_stock_price",
        "description": "Plot the stock price of a company over the last year",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol of of a company (e.g. AAPL for Apple Inc.)"
                }
            },
            "required": ["ticker"]
        },
    },
]

# we create a dictionary of available functions
available_functions = {
    'grt_stock_price': get_stock_price,
    'calculate_SMA': calculate_SMA,
    'calculate_EMA': calculate_EMA,
    'calculate_RSI': calculate_RSI,
    'calculate_MACD': calculate_MACD,
    'plot_stock_price': plot_stock_price
}

# we start building the streamlit application , and we keep track of messages in the session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []  # we create an empty list to store messages

st.title('Stock Market Chatbot')

user_input = st.text_input('your input')
if user_input:
    try:
        st.session_state['messages'].append({'role': 'user', 'content': f'{user_input}'})
        response = openai.ChatCompletion.create(
            model="gpt-3.5",
            messages=st.session_state['messages'],
            functions=functions,
            function_call='auto',
        )
        response_message = response['choices'][0]['message']

        if response_message.get('function_call'):
            function_name = response_message['function_call']['function']
            function_args = json.loads(response_message['function_call']['arguments'])
            if function_name in ['get_stock_price', 'calculate_RSI', 'calculate_MACD', 'plot_stock_price']:
                args_dict = {'ticker': function_args.get('ticker')}
            elif function_name in ['calculate_EMA', 'calculate_SMA']:
                args_dict = {'ticker': function_args.get('ticker'), 'window': function_args.get('window')}

            function_to_call = available_functions[function_name]
            function_reponse = function_to_call(**args_dict)

            if function_name == 'plot_stock_price':
                st.image('stock.png')
            else:
                st.session_state['messages'].append(response_message)
                st.session_state['messages'].append({
                    'role': 'function',
                    "name": function_name,
                    "content": function_reponse

                })
                second_response = openai.ChatCompletion.create(
                    model="gpt-3.5",
                    messages=st.session_state['messages'],

                )
                st.text(second_response['choices'][0]['message']['content'])
                st.session_state['messages'].append(
                    {'role': 'assistant', 'content': second_response['choices'][0]['message']['content']})
        else:
            st.text(response_message['content'])
            st.session_state['messages'].append({'role': 'assistant', 'content': response_message['content']})
    except:
        st.text('An error occured, please try again')
