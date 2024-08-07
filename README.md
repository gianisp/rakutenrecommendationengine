# AI-Powered Book Recommendation App

This application is an AI-powered book recommendation system that uses natural language processing to engage in conversations with users and provide personalized book recommendations based on the conversation context.

## Features

- Natural language conversation using Hugging Face's Inference API
- Book recommendations from the Rakuten Books API
- Flask-based backend for handling API requests
- Simple HTML/JavaScript frontend for user interaction

## Tech Stack

- Backend: Python with Flask
- Frontend: HTML, JavaScript
- APIs:
  - Hugging Face Inference API for natural language processing
  - Rakuten Books API for book recommendations

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7+
- pip (Python package manager)
- Rakuten API credentials
- Hugging Face API credentials

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-book-recommendations.git
   cd ai-book-recommendations
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   RAKUTEN_APP_ID=your_rakuten_app_id
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   ```

## Usage

1. Start the Flask server:
   ```
   python backend.py
   ```

2. Open a web browser and navigate to `http://localhost:8080` to use the application.

## Contributing

Contributions to this project are welcome. Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Hugging Face](https://huggingface.co/) for providing the Inference API
- [Rakuten](https://www.rakuten.com/) for their Books API
