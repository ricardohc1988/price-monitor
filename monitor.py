import pandas as pd
import time
import random
import asyncio
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from amazon_scraper import get_amazon_price
from ml_scraper import get_ml_price
from notifier import send_telegram_alert

# Logger configuration
def setup_logger():
    logger = logging.getLogger('price_monitor')
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    file_handler = RotatingFileHandler(
        'price_monitor.log', 
        maxBytes=1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

def read_products_from_xlsx(filepath):
    """Reads product data from Excel file"""
    return pd.read_excel(filepath)

def write_products_to_xlsx(filepath, df):
    """Writes updated product data back to Excel file"""
    df.to_excel(filepath, index=False)

def clean_price(price_str):
    """Converts price string to float by removing currency symbols"""
    try:
        return float(price_str.replace("$", "").replace(",", "").strip())
    except:
        return None

def get_last_recorded_price(row, current_column):
    """Gets the most recent historical price from the DataFrame"""
    price_columns = [col for col in row.index if col not in ['name', 'url'] and col != current_column]
    for col in reversed(price_columns):
        value = row[col]
        if pd.notnull(value):
            return value
    return None

async def monitor_prices(filepath):
    """Main function that orchestrates the price monitoring process"""
    logger.info("🚀 Starting price monitoring")
    
    # Read product data
    try:
        df = read_products_from_xlsx(filepath)
        logger.info(f"📊 Excel file loaded successfully: {len(df)} products")
    except Exception as e:
        logger.error(f"❌ Error reading Excel file: {str(e)}")
        return

    # Create timestamp column
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    if timestamp not in df.columns:
        df[timestamp] = None

    # Process each product
    for index, row in df.iterrows():
        name = row['name']
        url = row['url']
        
        logger.info(f"🔍 Processing product: {name}")
        logger.debug(f"URL: {url}")

        # Site-specific scraping
        try:
            if "amazon" in url:
                price_str = get_amazon_price(url)
                logger.debug(f"Amazon response: {price_str}")
            elif "mercadolibre" in url:
                price_str = get_ml_price(url)
                logger.debug(f"MercadoLibre response: {price_str}")
            else:
                logger.warning(f"⚠️ Unsupported website: {url}")
                continue
                
        except Exception as e:
            logger.error(f"❌ Error en scraping: {str(e)}")
            continue

        current_price = clean_price(price_str)
        last_price = get_last_recorded_price(row, current_column=timestamp)

        # Registro de precios
        if current_price is None:
            logger.warning(f"⚠️ Failed to get price for: {name}")
            if last_price is not None:
                logger.info(f"🔄 Using last recorded price: {last_price}")
                df.at[index, timestamp] = last_price
            continue
            
        logger.info(f"💰 Price obtained: {name} - ${current_price:.2f}")

        # Price drop alert
        if last_price is not None and current_price < last_price:
            alert_msg = f"📉 Price drop: {name} from ${last_price:.2f} to ${current_price:.2f}"
            logger.info(alert_msg)
            await send_telegram_alert(alert_msg, url=url)

        df.at[index, timestamp] = current_price

        # Random delay
        wait_time = random.uniform(5, 15)
        logger.debug(f"⏳ Waiting {wait_time:.2f} seconds...")
        time.sleep(wait_time)

    # Save updates
    try:
        write_products_to_xlsx(filepath, df)
        logger.info("💾 Data successfully saved to Excel")
    except Exception as e:
        logger.error(f"❌ Error saving Excel file: {str(e)}")

    logger.info("✅ Monitoring completed\n")

if __name__ == "__main__":
    asyncio.run(monitor_prices("products_example.xlsx"))
