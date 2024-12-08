# src/llm_integration.py

import logging
import openai
from typing import List, Dict
from src.logging_monitoring import logger
import os

class LLMIntegration:
    """
    Integrates with a Large Language Model (e.g., OpenAI GPT) to perform sentiment analysis on textual data.
    """
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize the LLMIntegration.
        
        :param api_key: OpenAI API key.
        :param model: LLM model to use.
        """
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key

    def analyze_sentiment(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Analyze sentiment of a list of texts using the LLM.
        
        :param texts: List of textual data (e.g., news headlines, articles).
        :return: List of dictionaries with sentiment scores.
        """
        sentiments = []
        for text in texts:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a sentiment analysis assistant."},
                        {"role": "user", "content": f"Analyze the sentiment of the following text and provide a score between -1 (negative) and 1 (positive):\n\n{text}"}
                    ],
                    max_tokens=10,
                    n=1,
                    stop=None,
                    temperature=0.0,
                )
                sentiment_score = float(response.choices[0].message['content'].strip())
                sentiments.append({"text": text, "sentiment_score": sentiment_score})
                logger.debug(f"Sentiment for text '{text}': {sentiment_score}")
            except Exception as e:
                logger.error(f"Error analyzing sentiment for text '{text}': {e}")
                sentiments.append({"text": text, "sentiment_score": 0.0})  # Neutral sentiment on error
        return sentiments

    def fetch_news(self, symbol: str, count: int = 10) -> List[str]:
        """
        Fetch recent news headlines related to a specific symbol.
        
        :param symbol: Trading symbol (e.g., 'BTCUSDT').
        :param count: Number of news headlines to fetch.
        :return: List of news headlines.
        """
        # Placeholder: Implement actual news fetching logic using an API like NewsAPI
        # For demonstration, returning mock data
        mock_headlines = [
            f"{symbol} hits new all-time high as market rallies.",
            f"Negative sentiment as {symbol} faces regulatory challenges.",
            f"{symbol} experiences volatility amid global economic shifts.",
            # Add more mock headlines as needed
        ][:count]
        logger.info(f"Fetched {len(mock_headlines)} news headlines for {symbol}")
        return mock_headlines

    def get_sentiment_scores(self, symbol: str, count: int = 10) -> float:
        """
        Get aggregated sentiment score for a specific symbol.
        
        :param symbol: Trading symbol.
        :param count: Number of news headlines to analyze.
        :return: Aggregated sentiment score.
        """
        headlines = self.fetch_news(symbol, count)
        sentiments = self.analyze_sentiment(headlines)
        if sentiments:
            avg_sentiment = sum(item["sentiment_score"] for item in sentiments) / len(sentiments)
            logger.info(f"Aggregated sentiment for {symbol}: {avg_sentiment}")
            return avg_sentiment
        else:
            logger.warning(f"No sentiments available for {symbol}. Returning neutral score.")
            return 0.0

# Example Usage
if __name__ == "__main__":
    # Ensure you have set your OpenAI API key as an environment variable
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        exit(1)
    
    llm = LLMIntegration(api_key=OPENAI_API_KEY)
    sentiment = llm.get_sentiment_scores("BTCUSDT", count=5)
    print(f"Aggregated Sentiment for BTCUSDT: {sentiment}")
