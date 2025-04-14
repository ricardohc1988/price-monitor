import requests
from bs4 import BeautifulSoup

def get_ml_price(url):
    """
    Retrieves the current price of a product on MercadoLibre Mexico.
    
    Args:
        url (str): Complete product URL on MercadoLibre Mexico
        
    Returns:
        str: Formatted price string (e.g. "$1,999.00") or error message if not found
        
    Raises:
        ConnectionError: If connection to MercadoLibre fails
        Exception: For other unexpected errors
    """
    
    # Configure headers to mimic a real browser visit
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.8"
    }

    try:
        # Make HTTP request with 10-second timeout
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises exception for HTTP errors
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, "lxml")

        # Primary method: Find meta tag with price information
        meta_price = soup.find("meta", itemprop="price")
        
        if meta_price and meta_price.get("content"):
            return f"${meta_price['content']}"
        else:
            # Fallback method: Check for alternative price elements
            span_price = soup.find("span", class_="andes-money-amount__fraction")
            if span_price:
                return f"${span_price.text.strip()}"
            return "Price not available"
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error with MercadoLibre: {str(e)}")
        return "Connection error"
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return "Error retrieving price"

if __name__ == "__main__":
    # Test example (using a placeholder URL)
    test_url =  "https://www.mercadolibre.com.mx/lentes-de-sol-hawkers-one-raw-hombre-y-mujer-elige-tu-color-diseno-negro-negro/p/MLM32975249#polycard_client=search-nordic&searchVariation=MLM32975249&wid=MLM2876475704&position=6&search_layout=grid&type=product&tracking_id=cbad9bbd-04e8-4478-a207-ca11c84fc6dd&sid=search"
    print("[Test] MercadoLibre price:", get_ml_price(test_url))