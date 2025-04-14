import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent

def get_amazon_price(url):
    """
    Retrieves the current price of a product on Amazon Mexico with anti-bot measures.
    
    Args:
        url (str): Complete product URL on Amazon Mexico
        
    Returns:
        str: Formatted price string (e.g. "$1,999.00") or error message if not found
        
    Raises:
        ConnectionError: If connection to Amazon fails
        Exception: For other unexpected errors
    """
    
    # Configure random delay between requests (1-5 seconds)
    time.sleep(random.uniform(1, 5))
    
    # Generate random User-Agent
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1"
    }

    try:
        # Create session to maintain cookies
        session = requests.Session()
        
        # Make HTTP request with timeout and retries
        response = session.get(
            url, 
            headers=headers, 
            timeout=10,
            allow_redirects=True
        )
        
        # Verify status code (including potential soft 404s)
        if response.status_code != 200:
            return f"HTTP Error: {response.status_code}"
            
        # Check for Amazon bot detection
        if "Enter the characters you see below" in response.text:
            return "Amazon CAPTCHA triggered - Bot detection active"
            
        # Parse HTML content
        soup = BeautifulSoup(response.content, "lxml")
        
        # Try multiple price selectors
        price_selectors = [
            "span.a-offscreen",
            "span.aok-offscreen",
            "span.a-price-whole",
            "span.apexPriceToPay span.a-offscreen",
            "span.priceToPay span.a-offscreen",
            "div.a-section span.a-color-price"
        ]

        for selector in price_selectors:
            try:
                price_tag = soup.select_one(selector)
                print(f"Testing selector '{selector}': {'Found' if price_tag else 'Not found'}")
                
                if price_tag:
                    price_text = price_tag.get_text(strip=True)
                    if price_text and any(c.isdigit() for c in price_text):
                        cleaned_price = ''.join(c for c in price_text if c.isdigit() or c in '.,')
                        if cleaned_price:
                            return f"${cleaned_price}"
            except Exception as e:
                print(f"Error testing selector {selector}: {str(e)}")
                continue
        
        print("DEBUG - Price not found. Saving HTML for review...")
        with open("amazon_debug.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        return "Price not available"
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {str(e)}")
        return "Connection error"
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return "Error retrieving price"

if __name__ == "__main__":
    # Test example with error handling
    test_urls = [
        "https://www.amazon.com.mx/dp/B0921PZ1WN/?coliid=I39T5OQSYV1T8M&colid=3R6VXQDSBN084&ref_=list_c_wl_lv_ov_lig_dp_it&th=1&psc=1",  # Standard product
        "https://www.amazon.com.mx/dp/B0C6CN56Y3/ref=twister_B0C6CXZSFR?th=1&psc=1",  # Different product
        "https://www.amazon.com.mx/dp/B09XBW4F8M?tag=ofertones03-20&linkCode=ogi&th=1&psc=1"
        "https://www.amazon.com.mx/SAMSUNG-Audifonos-inal%C3%A1mbricos-Nacional-Garant%C3%ADa/dp/B0D7FD2LGW/ref=pd_ci_mcx_mh_mcx_views_0_title?pd_rd_w=MSVLI&content-id=amzn1.sym.a5818c22-cc92-423d-abb2-e3ba2c7f6579%3Aamzn1.symc.40e6a10e-cbc4-4fa5-81e3-4435ff64d03b&pf_rd_p=a5818c22-cc92-423d-abb2-e3ba2c7f6579&pf_rd_r=N0AF2PSEN0D38RFY5W6M&pd_rd_wg=oFO5A&pd_rd_r=3e715634-2551-419d-b983-950e1d634ec9&pd_rd_i=B0D7FD2LGW&th=1"
    ]
    
    for url in test_urls:
        try:
            print(f"\nFetching price from: {url}")
            price = get_amazon_price(url)
            print(f"Price: {price}")
            # Extra delay between test requests
            time.sleep(random.uniform(2, 6))
        except Exception as e:
            print(f"Test failed for {url}: {str(e)}")