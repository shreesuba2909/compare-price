import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.flipkart.com" 
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8,application/json",
    "accept-language": "en-US,en;q=0.5",
    "accept-encoding": "gzip, deflate, br, zstd",
}

def scrape_flipkart(query):
    results = []
    product_links = getlinks(query)
    #print size of product links
    #save the product links in a file
    
    for link in product_links:
        product_data = extract_product_info(link)
        if product_data:
            results.append(product_data)

    return results      

def getlinks(query):
    seen_urls = set()
    page_number = 1
    #if query has space replace it with + sign
    query = query.replace(" ", "+")
    search_url = f"https://www.flipkart.com/search?q={query}"
    print(search_url)
    try:
        response = requests.get(search_url, headers=BASE_HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        product_links = []
        link_count = 0
        for div in soup.find_all("div", attrs={"class": "_75nlfW"}):
            a_tag = div.find_all("a", href=True)
            for a in a_tag:
                full_url = BASE_URL + a['href'] if "https" not in a['href'] else a['href']
                # print("full_url", full_url)
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    product_links.append(full_url)
                    link_count += 1
                if link_count == 15:
                    break
            if link_count == 15:
                break

        return product_links

    except Exception as e:
        print(f"Error fetching product links: {e}")
        return []   

seen_ids = set()

def extract_product_info(product_url):
    try:
        response = requests.get(product_url, headers=BASE_HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        script = soup.find("script", attrs={"id": "jsonLD"})
        if script is None:
            return None

        data = json.loads(script.string)
        
        # Extracting the required fields
        product_info = {}
        for item in data:
            if item["@type"] == "Product":
                product_name = item["name"] if "name" in item else "N/A"
                product_name = " ".join(product_name.split()[:10]) # trim product name to first 15 words
                image_url = item["image"] if "image" in item else "N/A"
                product_info = {
                    "price": item["offers"]["price"] if "offers" in item else "N/A",
                    "rating_count": item["aggregateRating"]["reviewCount"] if "aggregateRating" in item else 0,
                    "avg_rating": item["aggregateRating"]["ratingValue"] if "aggregateRating" in item else 0,
                    "product_name": product_name,
                    "image_url": image_url,
                    "brand_name": item["brand"]["name"] if "brand" in item else "N/A",
                    "product_url": product_url,
                    "logo": "https://rukminim1.flixcart.com/www/512/512/promos/11/07/2024/e8f26305-4b9f-444f-a970-b70dc51e04ef.png"
                }
                break

        return product_info
    except Exception as e:
        print(f"Error fetching product info: {e}")
        return None
