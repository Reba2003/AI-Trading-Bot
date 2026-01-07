# AI-Trading-Bot
I built a Python-based AI trading bot featuring a custom user interface and automated execution.

# About the bot
The project utilizes the Tkinter library to build a dashboard where users can manage equity positions, set position sizes, and monitor a Martingale DCA strategy. By integrating the Alpaca API, the bot establishes a live connection to brokerage services for real-time data fetching and order placement.A sophisticated Large Language Model (LLM) component is incorporated to serve as an AI portfolio manager, providing risk exposure analysis and strategic insights. The system also includes a persistent data storage feature using JSON files to save and load user configurations between sessions.

# bot.py:
The main Python script that contains the core logic for the user interface (GUI), the trading strategy, and the integration of various API components.
# alpaca.ipynb:
Jupyter notebook specifically for the Alpaca API, used to walk through the initial connection to the brokerage and test live data fetching before integrating those functions into the main bot script.
# openai.iynb:
Second Jupyter notebook is created to test and integrate the OpenAI API, allowing me to verify the AI's ability to analyze portfolio data and respond to messages before finalizing the code in the main application
