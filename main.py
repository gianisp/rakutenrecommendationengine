import os
import logging
from flask import Flask, request, jsonify, send_from_directory
import requests
import random
from collections import Counter

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

RAKUTEN_API_URL = "https://app.rakuten.co.jp/services/api/BooksBook/Search/20170404"
RAKUTEN_APP_ID = os.environ['RAKUTEN_APP_ID']
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
HUGGINGFACE_API_KEY = os.environ['HUGGINGFACE_API_KEY']

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        logging.info(f"Received user message: {user_message}")

        ai_response = get_ai_response(user_message)
        logging.info(f"AI response: {ai_response}")

        keywords = extract_keywords(user_message + " " + ai_response)
        logging.info(f"Extracted keywords: {keywords}")

        books = get_book_recommendations(keywords)
        logging.info(f"Found {len(books)} book recommendations")

        response = f"{ai_response}\n\nBased on our conversation, I've found some book recommendations for you."
        return jsonify({"response": response, "books": books})
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "An error occurred processing your request"}), 500

def get_ai_response(message):
    try:
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        payload = {"inputs": message}
        logging.info(f"Sending request to Hugging Face API with payload: {payload}")
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
        logging.info(f"Received response from Hugging Face API. Status code: {response.status_code}")

        if response.status_code != 200:
            logging.error(f"Hugging Face API error. Status code: {response.status_code}, Response: {response.text}")
            return "I'm having trouble understanding right now. Let's talk about books in general."

        response_json = response.json()
        logging.info(f"Parsed JSON response: {response_json}")

        return response_json[0].get('generated_text', "I'm sorry, I couldn't generate a response.")
    except Exception as e:
        logging.error(f"Error in get_ai_response: {str(e)}")
        return "I'm having trouble understanding right now. Let's talk about books in general."

def extract_keywords(text):
    # List of potential keywords (expand this list as needed)
    potential_keywords = ['fiction', 'non-fiction', 'mystery', 'science', 'history', 'romance', 'fantasy', 'biography',
                          'adventure', 'thriller', 'horror', 'comedy', 'drama', 'action', 'classics', 'contemporary',
                          'young adult', 'children', 'self-help', 'business', 'cooking', 'travel', 'art', 'music',
                          'philosophy', 'religion', 'psychology', 'technology', 'nature', 'sports']

    # Find all matching keywords in the text
    words = text.lower().split()
    found_keywords = [keyword for keyword in potential_keywords if keyword in words]

    # If no keywords found, return the most common words (excluding stop words)
    if not found_keywords:
        stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        word_counts = Counter(word for word in words if word not in stop_words)
        found_keywords = [word for word, _ in word_counts.most_common(3)]

    return found_keywords if found_keywords else ['popular']

def get_book_recommendations(keywords):
    all_recommendations = []
    used_titles = set()

    for keyword in keywords:
        params = {
            'format': 'json',
            'applicationId': RAKUTEN_APP_ID,
            'keyword': keyword,
            'hits': 30,
            'sort': 'standard',  # Changed from 'relevance' to 'standard'
            'availability': 1
        }

        try:
            response = requests.get(RAKUTEN_API_URL, params=params)
            response.raise_for_status()

            data = response.json()
            books = data.get('Items', [])

            logging.info(f"Received {len(books)} books for keyword '{keyword}'")

            for book in books:
                item = book['Item']
                title = item['title']
                if title not in used_titles:
                    all_recommendations.append({
                        'title': title,
                        'author': item.get('author', 'Unknown author'),
                        'price': f"¥{item.get('itemPrice', 'Price not available')}",
                        'imageUrl': item.get('largeImageUrl', ''),
                        'keyword': keyword
                    })
                    used_titles.add(title)

        except requests.RequestException as e:
            logging.error(f"Error fetching recommendations for keyword '{keyword}' from Rakuten API: {str(e)}")

    # Ensure we have a mix of books from different keywords
    random.shuffle(all_recommendations)
    final_recommendations = []
    keyword_count = {}

    for book in all_recommendations:
        keyword = book['keyword']
        if keyword_count.get(keyword, 0) < 2:  # Limit to 2 books per keyword
            final_recommendations.append(book)
            keyword_count[keyword] = keyword_count.get(keyword, 0) + 1

        if len(final_recommendations) >= 10:  # Limit to 10 total recommendations
            break

    logging.info(f"Final recommendations: {final_recommendations}")
    return final_recommendations

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)