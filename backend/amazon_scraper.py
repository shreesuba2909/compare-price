import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.amazon.in"
BASE_HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8,application/json",
    "accept-language": "en-US,en;q=0.5",
    "accept-encoding": "gzip, deflate, br, zstd",
}


def scrape_amazon(query):
    product_info = getProductInfo(query)
    return product_info
    
def getProductInfo(query):
    #if query has space replace it with + sign
    query = query.replace(" ", "+")
    search_url = f"https://www.amazon.in/s?k={query}"
    print(search_url)
    try:
        response = requests.get(search_url, headers=BASE_HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        product_count = 0
        products = soup.find("div", attrs={"class": "s-main-slot s-result-list s-search-results sg-row"})
        #save in products.html file 
        # with open("products.html", "w") as file:
        #     file.write(str(products))
        seen_urls = set()
        product_info_list = []
        for product in products.select("div.puis-card-container.s-card-container.s-overflow-hidden.aok-relative.puis-include-content-margin"):
            
            price = product.find("span", attrs={"class": "a-price-whole"}).get_text(strip=True) if product.find("span", attrs={"class": "a-price-whole"}) else "N/A"
            price = price.replace(",", "") if price != "N/A" else "N/A"
            price = price.replace(".", "")  if price != "N/A" else "N/A"
            price = int(price) if price.isdigit() else "N/A"


            #get all links of the product with class = "a-link-normal s-no-outline" where href exists
            product_link = product.find("a", class_="a-link-normal s-no-outline", href=True)['href'] if product.find("a", class_="a-link-normal s-no-outline", href=True) else "N/A"
            if(product_link == "N/A"):
                continue
            product_link = BASE_URL + product_link if not product_link.startswith("https://www.amazon.in") else product_link
            if product_link in seen_urls:
                continue
            seen_urls.add(product_link)
                
            rating_count_text = product.find("span", attrs={"class": "a-size-base"}).get_text(strip=True) if product.find("span", attrs={"class": "a-size-base"}) else "N/A"
            rating_count = ''.join(filter(str.isdigit, rating_count_text)) if rating_count_text != "N/A" else "N/A"
            rating_count = int(rating_count) if rating_count.isdigit() else 0

            avg_rating_text = product.find("span", attrs={"class": "a-icon-alt"}).get_text(strip=True) if product.find("span", attrs={"class": "a-icon-alt"}) else "N/A"
            avg_rating = avg_rating_text.split(" ")[0] if avg_rating_text != "N/A" else "N/A"
            avg_rating = float(avg_rating) if avg_rating.replace(".", "").isdigit() else 0

            product_name = product.find("img", attrs={"class": "s-image"})['alt'] if product.find("img", attrs={"class": "s-image"}) else "N/A"
            print(product_name)
            # if product name starts with Sponsored then skip
            if product_name.startswith("Sponsored"):
                continue
            # trim product name to first 10 words
            product_name = " ".join(product_name.split()[:10])

            product_info = {
               "price": price,
                "rating_count": rating_count,
                "avg_rating": avg_rating,
                "product_name": product_name,
                "image_url": product.find("img", attrs={"class": "s-image"}).get('src') if product.find("img", attrs={"class": "s-image"}) else "N/A",
                "product_url": product_link,
                "logo": "https://www.amazon.com/favicon.ico"
            }
            product_info_list.append(product_info)
            product_count += 1
            if product_count == 15:
                break
        return product_info_list
    except Exception as e:
        print(f"Error fetching product links: {e}")
        return []
