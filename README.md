# Price-monitor
This Python project monitors the prices of products from websites like Amazon and Mercado Libre. When a price drop is detected, it sends a Telegram alert.

## Features
- Monitors product prices from an Excel file.
- Supports Amazon and Mercado Libre product URLs.
- Automatic 5-15 second delays between requests to respect target websites
- Sends Telegram alerts when a price drop is detected.
- Stores historical price data in the Excel file.
- Built with pipenv for dependency management.

## Requirements
- Python 3.10 or higher
- A Telegram bot and your chat ID
- An Excel file named products.xlsx (use `products_example.xlsx` as template)

## Setup
1. Clone the repository
2. Install dependencies using pipenv
```sh
pipenv install
```
3. Activate the virtual environment
```
4. Create a config_private.py file with your Telegram bot token and chat ID:
```sh
TOKEN = "your-telegram-bot-token"
MY_CHAT_ID = "your-chat-id"
```
5. Run the script
```sh
python monitor.py
```

