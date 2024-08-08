import streamlit as st
import requests
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Set up your API keys
RAKUTEN_APP_ID = os.getenv('RAKUTEN_APP_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Import your functions from main.py
from main import get_ai_response, get_book_recommendations, extract_keywords

st.title("AI-Powered Book Recommendation App")

user_input = st.text_input("Enter your message:")

if st.button("Send"):
    try:
        st.write(f"You entered: {user_input}")

        # Get AI response
        ai_response = get_ai_response(user_input)
        st.write("AI Response:", ai_response)

        # Extract keywords
        keywords = extract_keywords(user_input + " " + ai_response)
        st.write("Extracted keywords:", keywords)

        # Get book recommendations
        books = get_book_recommendations(keywords)

        if books:
            st.write("Book Recommendations:")
            for book in books:
                st.write(f"- {book['title']} by {book['author']}")
                st.image(book['imageUrl'], width=100)
                st.write(f"  Price: {book['price']}")
        else:
            st.write("No book recommendations found.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logging.error(f"Error in processing request: {str(e)}", exc_info=True)

# Display API key status
st.sidebar.write("API Key Status:")
st.sidebar.write(f"RAKUTEN_APP_ID: {'Set' if RAKUTEN_APP_ID else 'Not Set'}")
st.sidebar.write(f"OPENAI_API_KEY: {'Set' if OPENAI_API_KEY else 'Not Set'}")