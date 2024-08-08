import os
import logging
from flask import Flask, request, jsonify, send_from_directory
import requests
import random
from collections import Counter
import openai  # Import the OpenAI library

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

RAKUTEN_API_URL = "https://app.rakuten.co.jp/services/api/BooksBook/Search/20170404"
RAKUTEN_APP_ID = os.environ['RAKUTEN_APP_ID']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']  # Use OPENAI_API_KEY now

def get_ai_response(message):
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")  # Get API key from environment variable

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use ChatGPT model
            messages=[
                {"role": "user", "content": message}  # Your message
            ],
            temperature=0.7,  # Adjust creativity (higher = more creative)
            max_tokens=100,  # Limit the response length
        )
        ai_response = response.choices[0].message.content
        return ai_response

    except Exception as e:
        logging.error(f"Error in get_ai_response: {str(e)}")
        return "I'm having trouble understanding right now. Let's talk about books in general."

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

def extract_keywords(text):
    # Add your keyword extraction logic here (e.g., using NLTK, spaCy, or other libraries)
    # Example using Counter for simple keyword extraction:
    words = text.lower().split()
    keyword_counts = Counter(words)
    keywords = [word for word, count in keyword_counts.items() if count > 1]
    return keywords

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)