# agents/chat_agent.py
import os
import re
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file for Gemini API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class ChatModerationAgent:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("Please set GEMINI_API_KEY in .env file")

        # Configure Gemini SDK
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def rule_based_check(self, message: str):
        """
        Simple rule-based checks:
        - Detect phone numbers
        - Detect spam keywords
        """
        # Phone number regex (Indian format + general numbers with 10+ digits)
        phone_pattern = re.compile(r"\b(?:\+91|0)?\s?\d{10}\b")
        if phone_pattern.search(message):
            return {"status": "PhoneNumber", "reason": "Message contains a phone number."}

        # Very simple spam word check
        spam_keywords = ["buy now", "free", "offer", "limited", "click here", "visit link"]
        if any(word in message.lower() for word in spam_keywords):
            return {"status": "Spam", "reason": "Message contains spam keywords."}

        return None  # if nothing matched

    def llm_moderation(self, message: str):
        """
        Use Gemini LLM to classify chat message
        """
        prompt = f"""
        You are a chat moderation agent for a marketplace.
        Classify the following message into one of:
        - Safe
        - Abusive
        - Spam

        Message: "{message}"

        Respond ONLY in JSON format:
        {{
          "status": "Safe" | "Abusive" | "Spam",
          "reason": "short explanation"
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            completion_text = response.text.strip()

            # Handle markdown formatting from LLM
            if completion_text.startswith("```"):
                completion_text = completion_text.strip("`")
                if "json" in completion_text:
                    completion_text = completion_text.replace("json", "", 1).strip()

            return json.loads(completion_text)
        except Exception as e:
            print(f"LLM moderation failed: {e}")
            return None

    def moderate(self, message: str):
        """
        Combine rule-based + LLM moderation
        """
        # 1. Rule-based checks (phone, spam keywords)
        rb_result = self.rule_based_check(message)
        if rb_result:
            return rb_result

        # 2. LLM classification
        llm_result = self.llm_moderation(message)
        if llm_result:
            llm_result["reason"] = f"LLM + rule-based fallback: {llm_result['reason']}"
            return llm_result

        # 3. Default safe if all else fails
        return {"status": "Safe", "reason": "Defaulted to Safe (no issues found)"}


# Example usage
if __name__ == "__main__":
    agent = ChatModerationAgent()
    messages = [
        "Hello, is this still available?",
        "Call me at 9876543210",
        "Buy now, limited offer, click here!",
        "You are an idiot, waste of time!"
    ]
    for msg in messages:
        print(msg, "=>", agent.moderate(msg))