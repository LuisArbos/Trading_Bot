# Trading Bot

This project is an automated trading bot that uses technical indicators to make trading decisions. The bot is designed to trade on Binance and OKX exchanges based on the following indicators:

- **Bollinger Bands**: Used to measure market volatility and identify overbought or oversold conditions.
- **Relative Strength Index (RSI)**: A momentum oscillator that measures the speed and change of price movements, indicating overbought or oversold conditions.
- **Moving Average Convergence Divergence (MACD)**: A trend-following momentum indicator that shows the relationship between two moving averages of a security's price.

## Project Structure

- **binance_files/**: Contains Binance-specific functions and analysis notebooks.
- **okx_files/**: Contains OKX-specific functions and analysis notebooks.
- **strategies/**: Contains trading strategies implemented in Python.
- **credentials.env**: Environment variables for API keys and other secrets.
- **main.py**: The main script to run the trading bot.
- **requirements.txt**: Lists the project's dependencies.
- **README.md**: This file.

## Setup and Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/LuisArbos/Trading_Bot.git
    cd TradingBot
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the environment variables**:
    - Rename `credentials.env.example` to `credentials.env`.
    - Fill in your API keys and other credentials in the `credentials.env` file.

5. **Run the bot**:
    ```bash
    python main.py
    ```

## Usage

The bot uses three main indicators to make trading decisions:

1. **Bollinger Bands**: Detects volatility and potential reversal points.
2. **RSI**: Identifies overbought and oversold conditions.
3. **MACD**: Confirms trends and momentum.

You can customize the strategy in `strategies/strategy.py` to fit your trading needs.
