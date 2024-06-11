# Stock Market Chatbot

This is a chatbot which is specially meant for stock market questions and it can even return the price history of the stock over the period of time we specify ans also can predict to buy or not.
<h5>Used Libraries</h5>
Made purely in python and uses library openai for the chatbot intelligence , streamlit for the web application , yfinannce library and pandas.
But firstly to use the chatbot one needs to generate a key of his own from https://platform.openai.com/docs/overview 
To generate a key go to your account and create a personal key then enter the billing details <b>And then purchase some credits , Minimum is 5 USD or approx 500 INR</b>
ans then enter you key ina text file ans then read the text file in it sa given in the code.
<h5>Structure</h5>
First we have all the financial functions defined to get stock price and to calculate SMA , EMA , RSI , MACD and also a function to plot the stock price.
Only input we need to give the functions are ticker. As the application is powered by openAI api even if we enter any question it will return a result which will be satisfactory.
Example. Even on asking give me the current stock price of company founded by Steve Jobs -> It will return the AAPL stock and we can even ask wether the stock will give profit over the course of specified time.
