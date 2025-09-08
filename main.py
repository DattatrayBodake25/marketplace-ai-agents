# main.py
import os
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# Import our agents
from agents.price_agent import PriceSuggestorAgent
from agents.chat_agent import ChatModerationAgent
from agents.recommendation_agent import RecommendationAgent
from utils.logger import Logger

# Load Dataset
data_path = os.path.join("data", "products.csv")
df = pd.read_csv(data_path)

# Initialize Agents
price_agent = PriceSuggestorAgent()
chat_agent = ChatModerationAgent()
recommendation_agent = RecommendationAgent(dataset_path=data_path)

# Initialize Logger (singleton)
logger = Logger()

# FastAPI App
app = FastAPI(title="Marketplace AI Agents")

# Request Schemas
class ProductRequest(BaseModel):
    title: str
    category: str
    brand: str
    condition: str
    age_months: int
    asking_price: float
    location: str

class ChatRequest(BaseModel):
    message: str

# Routes
@app.post("/negotiate")
def negotiate_price(product: ProductRequest):
    """
    Suggest price for a product using PriceSuggestorAgent
    and log the negotiation.
    """
    result = price_agent.suggest_price(product.dict())
    # Log the negotiation
    logger.log_negotiation(product_input=product.dict(), product_id=None, result=result)
    return result

@app.get("/negotiate/{product_id}")
def negotiate_by_id(product_id: int):
    """
    Suggest price for a product directly from dataset by product_id
    """
    product = df[df["id"] == product_id]
    if product.empty:
        return {"error": f"Product with id {product_id} not found."}
    product_dict = product.iloc[0].to_dict()
    result = price_agent.suggest_price(product_dict)
    # Log the negotiation
    logger.log_negotiation(product_input=product_dict, product_id=product_id, result=result)
    return {"product": product_dict, "suggestion": result}

@app.post("/moderate")
def moderate_chat(chat: ChatRequest):
    """
    Moderate a chat message and log the result
    """
    result = chat_agent.moderate(chat.message)
    logger.log_moderation(message=chat.message, result=result)
    return result

@app.get("/recommend/{product_id}")
def recommend_product(product_id: int, top_n: int = 3):
    """
    Recommend similar products from dataset
    """
    recs = recommendation_agent.recommend(product_id=product_id, top_n=top_n)
    return recs

# Debug Endpoint (optional)
@app.get("/sample-product")
def get_sample_product():
    """Return first product from dataset as JSON"""
    return df.iloc[0].to_dict()














# # main.py
# import os
# import pandas as pd
# from fastapi import FastAPI
# from pydantic import BaseModel

# # Import our agents
# from agents.price_agent import PriceSuggestorAgent
# from agents.chat_agent import ChatModerationAgent

# # Load Dataset
# data_path = os.path.join("data", "products.csv")
# df = pd.read_csv(data_path)

# # Initialize Agents
# price_agent = PriceSuggestorAgent()
# chat_agent = ChatModerationAgent()

# # FastAPI App
# app = FastAPI(title="Marketplace AI Agents")

# # Request Schemas
# class ProductRequest(BaseModel):
#     title: str
#     category: str
#     brand: str
#     condition: str
#     age_months: int
#     asking_price: float
#     location: str

# class ChatRequest(BaseModel):
#     message: str

# # Routes
# @app.post("/negotiate")
# def negotiate_price(product: ProductRequest):
#     result = price_agent.suggest_price(product.dict())
#     return result

# @app.post("/moderate")
# def moderate_chat(chat: ChatRequest):
#     result = chat_agent.moderate(chat.message)
#     return result

# # Debug Endpoint (optional)
# @app.get("/sample-product")
# def get_sample_product():
#     """Return first product from dataset as JSON"""
#     return df.iloc[0].to_dict()