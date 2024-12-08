# src/llm_integration.py

import openai
import os
import logging

logger = logging.getLogger(__name__)

class LLMIntegration:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY environment variable not set.")
            raise RuntimeError("OPENAI_API_KEY environment variable not set.")
        openai.api_key = self.api_key
        logger.info("LLMIntegration initialized with OpenAI API key.")
    
    def generate_strategy(self, prompt: str) -> str:
        """
        Generate a trading strategy based on the given prompt.
        
        :param prompt: User input prompt
        :return: Generated strategy as a string
        """
        try:
            logger.info("Generating strategy with prompt: %s", prompt)
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert trading strategist."},
                    {"role": "user", "content": prompt}
                ]
            )
            strategy = response.choices[0].message['content'].strip()
            logger.info("Strategy generated successfully.")
            return strategy
        except Exception as e:
            logger.error(f"LLMIntegration error: {e}")
            raise e
