# agents/price_agent.py
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file for Gemini API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class PriceSuggestorAgent:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("Please set GEMINI_API_KEY in .env file")

        # Configure Gemini SDK
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def rule_based_price(self, product):
        """
        Simple rule-based fallback price calculation
        """
        asking_price = product.get("asking_price", 1000)
        condition = product.get("condition", "Good").lower()
        age_months = product.get("age_months", 12)

        # Condition factor
        if condition == "like new":
            factor = 0.9
        elif condition == "good":
            factor = 0.75
        elif condition == "fair":
            factor = 0.6
        else:
            factor = 0.7  # default

        # Depreciation based on age (0.5% per month)
        depreciation = 1 - (age_months * 0.005)
        depreciation = max(depreciation, 0.5)  # min 50% value

        base_price = asking_price * factor * depreciation
        min_price = round(base_price * 0.95)
        max_price = round(base_price * 1.05)

        reason = (
            f"Rule-based: category {product.get('category')}, "
            f"condition {condition}, age {age_months} months."
        )
        return {"min_price": min_price, "max_price": max_price, "reason": reason}

    def llm_price(self, product):
        """
        Call Gemini API to suggest price using LLM
        """
        prompt = f"""
        You are a second-hand marketplace expert.
        Suggest a fair price range (min_price, max_price) for the following product.

        Product details:
        Title: {product.get('title')}
        Category: {product.get('category')}
        Brand: {product.get('brand')}
        Condition: {product.get('condition')}
        Age in months: {product.get('age_months')}
        Asking price: {product.get('asking_price')}
        Location: {product.get('location')}

        Respond ONLY with JSON in this exact format:
        {{
          "min_price": number,
          "max_price": number,
          "reason": "short explanation here"
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            completion_text = response.text.strip()

            # Try to find JSON inside response text
            if completion_text.startswith("```"):
                completion_text = completion_text.strip("`")  # remove markdown formatting
                if "json" in completion_text:
                    completion_text = completion_text.replace("json", "", 1).strip()

            return json.loads(completion_text)
        except Exception as e:
            print(f"LLM price suggestion failed: {e}")
            return None

    def suggest_price(self, product):
        """
        Combine rule-based and LLM suggestion
        + Fraud detection for unrealistic prices
        """
        # 1. Try LLM
        result = self.llm_price(product)
        if result:
            result["reason"] = f"LLM + rule-based fallback: {result['reason']}"
        else:
            # 2. Fallback to rule-based
            result = self.rule_based_price(product)

        # 3. Fraud detection logic
        asking_price = product.get("asking_price", 0)
        if asking_price > result["max_price"] * 1.5:
            result["fraud_flag"] = "Suspicious: Asking price way too high."
        elif asking_price < result["min_price"] * 0.5:
            result["fraud_flag"] = "Suspicious: Asking price way too low."
        else:
            result["fraud_flag"] = "Normal"

        return result


# Example usage
if __name__ == "__main__":
    agent = PriceSuggestorAgent()
    sample_product = {
        "title": "iPhone 12",
        "category": "Mobile",
        "brand": "Apple",
        "condition": "Good",
        "age_months": 24,
        "asking_price": 35000,
        "location": "Mumbai",
    }
    price_suggestion = agent.suggest_price(sample_product)
    print(price_suggestion)












# # agents/price_agent.py
# import os
# import json
# from dotenv import load_dotenv
# import google.generativeai as genai

# # Load .env file for Gemini API key
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# class PriceSuggestorAgent:
#     def __init__(self):
#         if not GEMINI_API_KEY:
#             raise ValueError("Please set GEMINI_API_KEY in .env file")

#         # Configure Gemini SDK
#         genai.configure(api_key=GEMINI_API_KEY)
#         self.model = genai.GenerativeModel("gemini-2.0-flash")

#     def rule_based_price(self, product):
#         """
#         Simple rule-based fallback price calculation
#         """
#         asking_price = product.get("asking_price", 1000)
#         condition = product.get("condition", "Good").lower()
#         age_months = product.get("age_months", 12)

#         # Condition factor
#         if condition == "like new":
#             factor = 0.9
#         elif condition == "good":
#             factor = 0.75
#         elif condition == "fair":
#             factor = 0.6
#         else:
#             factor = 0.7  # default

#         # Depreciation based on age (0.5% per month)
#         depreciation = 1 - (age_months * 0.005)
#         depreciation = max(depreciation, 0.5)  # min 50% value

#         base_price = asking_price * factor * depreciation
#         min_price = round(base_price * 0.95)
#         max_price = round(base_price * 1.05)

#         reason = (
#             f"Rule-based: category {product.get('category')}, "
#             f"condition {condition}, age {age_months} months."
#         )
#         return {"min_price": min_price, "max_price": max_price, "reason": reason}


#     def llm_price(self, product):
#         """
#         Call Gemini API to suggest price using LLM
#         """
#         prompt = f"""
#         You are a second-hand marketplace expert.
#         Suggest a fair price range (min_price, max_price) for the following product.

#         Product details:
#         Title: {product.get('title')}
#         Category: {product.get('category')}
#         Brand: {product.get('brand')}
#         Condition: {product.get('condition')}
#         Age in months: {product.get('age_months')}
#         Asking price: {product.get('asking_price')}
#         Location: {product.get('location')}

#         Respond ONLY with JSON in this exact format:
#         {{
#           "min_price": number,
#           "max_price": number,
#           "reason": "short explanation here"
#         }}
#         """

#         try:
#             response = self.model.generate_content(prompt)
#             completion_text = response.text.strip()

#             # Try to find JSON inside response text
#             if completion_text.startswith("```"):
#                 completion_text = completion_text.strip("`")  # remove markdown formatting
#                 if "json" in completion_text:
#                     completion_text = completion_text.replace("json", "", 1).strip()

#             return json.loads(completion_text)
#         except Exception as e:
#             print(f"LLM price suggestion failed: {e}")
#             return None


#     def suggest_price(self, product):
#         """
#         Combine rule-based and LLM suggestion
#         """
#         # 1. Try LLM
#         llm_result = self.llm_price(product)
#         if llm_result:
#             llm_result["reason"] = f"LLM + rule-based fallback: {llm_result['reason']}"
#             return llm_result

#         # 2. Fallback to rule-based
#         return self.rule_based_price(product)


# # Example usage
# if __name__ == "__main__":
#     agent = PriceSuggestorAgent()
#     sample_product = {
#         "title": "iPhone 12",
#         "category": "Mobile",
#         "brand": "Apple",
#         "condition": "Good",
#         "age_months": 24,
#         "asking_price": 35000,
#         "location": "Mumbai",
#     }
#     price_suggestion = agent.suggest_price(sample_product)
#     print(price_suggestion)