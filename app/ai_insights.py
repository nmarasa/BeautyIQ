import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_ai_insights(product_name, reviews_df):

    negative_reviews = reviews_df[
        (reviews_df["product_name"] == product_name) &
        (reviews_df["rating"] <= 3)
    ]["review_text"].dropna()

    if len(negative_reviews) == 0:
        return "Not enough negative reviews to generate AI insights."

    sample_size = min(20, len(negative_reviews))

    sample_reviews = negative_reviews.sample(
        n=sample_size,
        random_state=42
    )

    review_text = "\n\n".join(sample_reviews.tolist())

    response = client.responses.create(
        model="gpt-5-mini",
        input=f"""
You are analyzing customer reviews for a beauty company.

Product: {product_name}

Using only the customer reviews provided below:

1. Identify the 3 most common complaints.
2. Identify positive themes customers still mention.
3. Explain the main reason customers appear dissatisfied.
4. Give one actionable product improvement recommendation.

Do not invent information that is not supported by the reviews.
Keep the analysis concise and business-focused.

Customer reviews:
{review_text}
"""
    )

    return response.output_text