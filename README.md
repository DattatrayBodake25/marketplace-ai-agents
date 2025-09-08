# Marketplace AI Agents

This project is an AI-powered assistant for a second-hand marketplace. It provides **price suggestions, chat moderation, and product recommendations** using LLMs and rule-based agents. All features are exposed via **FastAPI endpoints**.

---

## Table of Contents

- [Project Overview](#project-overview)  
- [Features](#features)  
- [Folder Structure](#folder-structure)  
- [Tech Stack](#tech-stack)  
- [Setup Instructions](#setup-instructions)  
- [Environment Variables](#environment-variables)  
- [Dataset](#dataset)  
- [FastAPI Endpoints](#fastapi-endpoints)  
- [Logging](#logging)  
- [Testing](#testing)  
- [Future Improvements](#future-improvements)

---

## Project Overview

The goal of this project is to build **agents** that assist buyers and sellers in a second-hand marketplace:

1. **Price Suggestor Agent**  
   - Suggests fair market prices for second-hand products using a combination of **LLM (Google Gemini 2.0 Flash)** and **rule-based logic**.  
   
2. **Chat Moderation Agent**  
   - Detects whether chat messages are **Safe, Spam, Abusive, or contain a Phone Number**.  

3. **Recommendation Agent**  
   - Suggests **similar products** based on category, brand, condition, age, and price.  

All actions are **logged** into CSV and JSON for future analytics.

---

## Features

- Price suggestions with **fraud detection** (overpriced/underpriced items)  
- Chat moderation for marketplace safety  
- Product recommendation for better user experience  
- Endpoints for negotiation via **manual input** or **dataset ID**  
- Logging of all negotiations and moderation results (CSV + JSON)  
- FastAPI-based **REST API**  
- Easy testing with Postman  

---

## Folder Structure
```bash
marketplace_ai/
│
├── agents/
│ ├── price_agent.py                                                   # Price Suggestor Agent
│ ├── chat_agent.py                                                    # Chat Moderation Agent
│ └── recommendation_agent.py                                          # Recommendation Agent
│
├── data/
│ └── products.csv                                                     # Sample product dataset
│
├── logs/                                                              # Auto-created logs folder
│ ├── negotiation_log.csv
│ ├── negotiation_log.json
│ ├── moderation_log.csv
│ └── moderation_log.json
│
├── utils/
│ └── logger.py                                                        # Logging utility (singleton)
│
├── main.py                                                            # FastAPI entry point
├── .env                                                               # Environment variables (Gemini API key)
└── requirements.txt                                                   # Python dependencies
```
---

## Tech Stack

- **Python 3.11.9**  
- **FastAPI** – Web framework  
- **Google Gemini API (gemini-2.0-flash)** – LLM for price suggestion  
- **Pandas** – Dataset handling  
- **Pydantic** – Request validation  
- **CSV + JSON** – Logging  
- **Uvicorn** – ASGI server  

---

## Setup Instructions

1. **Clone repository**  
```bash
git clone https://github.com/DattatrayBodake25/marketplace-ai-agents
cd marketplace_ai
```

2. **Create virtual environment & activate**
```bash
python -m venv venv

source venv/bin/activate      # Linux/macOS

venv\Scripts\activate         # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
Create a .env file in the project root:
```bash
GEMINI_API_KEY=<YOUR_GOOGLE_GEMINI_API_KEY>
```

5. **Run FastAPI server**
```bash
uvicorn main:app --reload
```

6. **Server URL**
Open your browser or Postman:
```bash
http://127.0.0.1:8000
```

---

## Dataset

CSV file: `data/products.csv`
```bash
| id  | title          | category  | brand   | condition | age_months | asking_price | location |
|-----|----------------|-----------|---------|-----------|------------|--------------|----------|
| 1   | iPhone 12      | Mobile    | Apple   | Good      | 24         | 35000        | Mumbai   |
| 2   | Redmi Note 11  | Mobile    | Xiaomi  | Like New  | 8          | 11000        | Delhi    |
| 3   | OnePlus Nord 2 | Mobile    | OnePlus | Fair      | 30         | 15000        | Bangalore|
| 4   | Dell Inspiron  | Laptop    | Dell    | Good      | 36         | 28000        | Pune     |
| ... | ...            | ...       | ...     | ...       | ...        | ...          | ...      |
```

---

## FastAPI Endpoints
1. Negotiate Price (Manual Input):
- **URL:** `/negotiate`
- **Method:** `POST`
- **Request Body (JSON):**
```json
{
  "title": "iPhone 12",
  "category": "Mobile",
  "brand": "Apple",
  "condition": "Good",
  "age_months": 24,
  "asking_price": 35000,
  "location": "Mumbai"
}
```
- Response:
```json
{
  "min_price": 22000,
  "max_price": 27000,
  "reason": "LLM + rule-based fallback: ...",
  "fraud_flag": "Normal"
}
```

2. Negotiate Price by ID:
- **URL:** `/negotiate/{product_id}`
- **Method:** `GET`
- **Response:**
```json
{
  "product": { ... },
  "suggestion": {
    "min_price": 23000,
    "max_price": 28000,
    "reason": "...",
    "fraud_flag": "Normal"
  }
}
```

3. Moderate Chat:
- **URL:** `/moderate`
- **Method:** `POST`
- **Request Body (JSON):**
```json
{ "message": "Call me at 9876543210" }
```
- **Response:**
```json
{
  "status": "PhoneNumber",
  "reason": "Message contains a phone number."
}
```

4. Recommend Products:
- **URL:** `/recommend/{product_id}`
- **Method:** `GET`
- **Query Params:** `top_n (optional, default=3)`
- **Response:**
```json
{
  "product_id": 1,
  "title": "iPhone 12",
  "recommendations": [
    { "id": 6, "title": "Samsung Galaxy S21", "similarity": 2 },
    { "id": 3, "title": "OnePlus Nord 2", "similarity": 1 },
    { "id": 12, "title": "Motorola G60", "similarity": 1 }
  ]
}
```

5. Sample Product:
- **URL:** `/sample-product`
- **Method:** `GET`
- **Response:** `Returns first product in dataset.`
```json
{
    "id": 1,
    "title": "iPhone 12",
    "category": "Mobile",
    "brand": "Apple",
    "condition": "Good",
    "age_months": 24,
    "asking_price": 35000,
    "location": "Mumbai"
}
```

---

## Logging
All negotiation and moderation results are stored automatically in:
```pgsql
logs/
├── negotiation_log.csv
├── negotiation_log.json
├── moderation_log.csv
└── moderation_log.json
```
CSV + JSON format allows easy analytics or model retraining.

---

## Testing
1. Use Postman or curl for API requests.
2. All endpoints already included in Postman collection (see instructions above).
3. Validate:
   - /negotiate → price + fraud detection
   - /moderate → chat classification
   - /recommend/{product_id} → similar product suggestions
   - /sample-product → dataset check

---

## Future Improvements
- Integrate real-time web scraping (OLX, Cashify) for dynamic price suggestions.
- Multi-agent chat system for buyer-seller negotiation.
- Advanced fraud detection using ML models.
- Authentication & user profiles for marketplace security.

---

# Thank You!

---
