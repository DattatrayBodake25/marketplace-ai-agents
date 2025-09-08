# agents/recommendation_agent.py
import pandas as pd


class RecommendationAgent:
    def __init__(self, dataset_path="dataset.csv"):
        self.dataset_path = dataset_path
        self.dataset = pd.read_csv(dataset_path)

    def recommend(self, product_id, top_n=3):
        """
        Recommend similar products from dataset
        """
        # Find target product
        product = self.dataset[self.dataset["id"] == product_id]
        if product.empty:
            return {"error": f"Product with id {product_id} not found."}

        product = product.iloc[0]

        # Filter by category
        same_category = self.dataset[
            (self.dataset["category"] == product["category"])
            & (self.dataset["id"] != product_id)
        ].copy()

        # Add similarity score
        def score(row):
            score = 0
            if row["brand"] == product["brand"]:
                score += 2
            if abs(row["age_months"] - product["age_months"]) <= 12:
                score += 1
            if abs(row["asking_price"] - product["asking_price"]) <= 5000:
                score += 1
            return score

        same_category["similarity"] = same_category.apply(score, axis=1)

        # Sort by similarity & pick top_n
        recommendations = (
            same_category.sort_values(by="similarity", ascending=False)
            .head(top_n)
            .to_dict(orient="records")
        )

        return {
            "product_id": int(product_id),
            "title": product["title"],
            "recommendations": recommendations,
        }


# Example usage
if __name__ == "__main__":
    agent = RecommendationAgent("dataset.csv")
    result = agent.recommend(1, top_n=3)
    import json

    print(json.dumps(result, indent=2))