from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
# from walmart_scraper import scrape_walmart
from amazon_scraper import scrape_amazon
from flipkart_scraper import scrape_flipkart
import os
import json

app = Flask(__name__, static_folder="../frontend", static_url_path="", template_folder="../frontend")

# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}}, 
     supports_credentials=True, 
     methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Origin", "Content-Type", "Accept"])

OUTPUT_FILE = "/app/frontend/product_info.jsonl"

@app.route('/')
def serve_index():
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Invalid request. Provide 'query' in JSON payload."}), 400

    query = data["query"]
    print(f"Received search query: {query}")

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print(f"Deleted existing file: {OUTPUT_FILE}")

    results = []

    for platform, scraper in {
        "Amazon": scrape_amazon,
        "Flipkart": scrape_flipkart,
        # "Walmart": scrape_walmart,
    }.items():
        try:
            print(f"Scraping {platform} for query: {query}")
            site_results = scraper(query)
            if site_results:
                print(f"Scraped {len(site_results)} results from {platform}")
                results.extend(site_results)
            else:
                print(f"No results found for {platform}")

        except Exception as e:
            print(f"Error scraping {platform}: {e}")

    if results:
        with open(OUTPUT_FILE, 'w') as file:
            for product in results:
                file.write(json.dumps(product) + "\n")
        print(f"Saved results to file: {OUTPUT_FILE}")

    return jsonify({
        "message": "Query processed successfully.",
        "results_saved_to": OUTPUT_FILE,
        "total_results": len(results),
    }), 200

@app.route('/product_info')
def serve_product_info():
    return send_from_directory(app.static_folder, 'product_info.jsonl')

if __name__ == "__main__":
    app.run(debug=True, port=5000)