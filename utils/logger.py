# utils/logger.py
import os
import csv
import json
from datetime import datetime

class Logger:
    _instance = None  # Singleton instance

    def __new__(cls, log_dir="logs"):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._init(log_dir)
        return cls._instance

    def _init(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        # Define file paths
        self.negotiation_log_csv = os.path.join(log_dir, "negotiation_log.csv")
        self.moderation_log_csv = os.path.join(log_dir, "moderation_log.csv")
        self.negotiation_log_json = os.path.join(log_dir, "negotiation_log.json")
        self.moderation_log_json = os.path.join(log_dir, "moderation_log.json")

        # Ensure CSV headers exist
        self._init_csv(self.negotiation_log_csv, ["timestamp", "product_id", "input", "output"])
        self._init_csv(self.moderation_log_csv, ["timestamp", "message", "output"])

    def _init_csv(self, filepath, headers):
        if not os.path.exists(filepath):
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)

    def log_negotiation(self, product_id, product_input, result):
        timestamp = datetime.now().isoformat()
        row = [timestamp, product_id, json.dumps(product_input), json.dumps(result)]

        # Append to CSV
        with open(self.negotiation_log_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        # Append to JSON
        self._append_json(self.negotiation_log_json, {
            "timestamp": timestamp,
            "product_id": product_id,
            "input": product_input,
            "output": result
        })

    def log_moderation(self, message, result):
        timestamp = datetime.now().isoformat()
        row = [timestamp, message, json.dumps(result)]

        # Append to CSV
        with open(self.moderation_log_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        # Append to JSON
        self._append_json(self.moderation_log_json, {
            "timestamp": timestamp,
            "message": message,
            "output": result
        })

    def _append_json(self, filepath, entry):
        data = []
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []

        data.append(entry)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


# Example usage
if __name__ == "__main__":
    logger = Logger()  # Singleton instance

    # Log a negotiation example
    sample_product = {
        "title": "iPhone 12",
        "category": "Mobile",
        "brand": "Apple",
        "condition": "Good",
        "age_months": 24,
        "asking_price": 35000,
        "location": "Mumbai",
    }
    result = {"min_price": 22000, "max_price": 27000, "reason": "Test log"}
    logger.log_negotiation(1, sample_product, result)

    # Log a moderation example
    message = "Call me at 9876543210"
    moderation_result = {"status": "PhoneNumber", "reason": "Message contains a phone number."}
    logger.log_moderation(message, moderation_result)

    print("✅ Logs written to /logs directory")