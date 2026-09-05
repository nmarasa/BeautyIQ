import streamlit as st
import pandas as pd
from app.ai_insights import generate_ai_insights

reviews = pd.read_csv(
    "data/processed/skincare_reviews_clean.csv"
)

all_diagnostics = pd.read_csv(
    "data/processed/all_product_diagnostics.csv"
)

diagnostics = pd.read_csv(
    "data/processed/product_diagnostics.csv"
)

complaint_themes = {
    "dryness": [
        "dry", "drying", "dried", "dehydrated"
    ],
    "irritation": [
        "irritated", "irritation", "burning", "burned", "sting", "stinging"
    ],
    "breakouts": [
        "breakout", "breakouts", "broke out", "acne", "pimples"
    ],
    "ineffective": [
        "didn work", "doesn work", "no difference", "not effective"
    ],
    "value": [
        "waste money", "not worth", "too expensive", "overpriced"
    ],
    "texture": [
        "sticky", "greasy", "oily", "heavy", "thick"
    ],
    "smell": [
        "smell", "scent", "fragrance"
    ],
    "packaging": [
        "pump", "bottle", "packaging", "container", "leak"
    ]
}

st.set_page_config(
    page_title="BeautyIQ",
    layout="wide"
)

products = pd.read_csv("data/processed/products_clean.csv")
opportunities = pd.read_csv("data/processed/opportunity_ranking.csv")

st.title("BeautyIQ")

st.write(
    "Beauty product intelligence dashboard for identifying "
    "customer pain points and product opportunities."
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Products Analyzed",
    f"{len(products):,}"
)

col2.metric(
    "Brands",
    f"{products['brand_name'].nunique():,}"
)

col3.metric(
    "Avg Product Rating",
    f"{products['rating'].mean():.2f}"
)

st.metric(
    "Products With Meaningful Signals",
    len(diagnostics)
)


st.subheader("Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

brand_options = ["All"] + sorted(opportunities["brand_name"].dropna().unique().tolist())

selected_brand = filter_col1.selectbox(
    "Brand",
    brand_options
)

max_price = filter_col2.slider(
    "Maximum Price",
    min_value=0,
    max_value=int(opportunities["price_usd"].max()),
    value=int(opportunities["price_usd"].max())
)

max_rating = filter_col3.slider(
    "Maximum Rating",
    min_value=1.0,
    max_value=5.0,
    value=4.1,
    step=0.1
)

filtered_opportunities = opportunities.copy()

if selected_brand != "All":
    filtered_opportunities = filtered_opportunities[
        filtered_opportunities["brand_name"] == selected_brand
    ]

filtered_opportunities = filtered_opportunities[
    (filtered_opportunities["price_usd"] <= max_price) &
    (filtered_opportunities["average_rating"] <= max_rating)
]


display_df = filtered_opportunities[
    [
        "product_name",
        "brand_name",
        "price_usd",
        "average_rating",
        "total_reviews",
        "top_complaint",
        "top_complaint_pct",
        "top_praise",
        "top_praise_pct",
        "opportunity_score"
    ]
].copy()



st.subheader("Products With Unusually High Complaint Signals")

filtered = diagnostics.copy()

if selected_brand != "All":
    filtered = filtered[
        filtered["brand_name"] == selected_brand
    ]

filtered = filtered[
    (filtered["price_usd"] <= max_price) &
    (filtered["rating"] <= max_rating)
]

st.caption(
    f"Showing {len(filtered):,} products with meaningful complaint signals"
)

display_df = filtered[
    [
        "product_name",
        "brand_name",
        "price_usd",
        "rating",
        "reviews",
        "theme",
        "percent_of_reviews_product",
        "percent_of_reviews_baseline",
        "lift",
        "issue_strength"
    ]
].rename(
    columns={
        "product_name": "Product",
        "brand_name": "Brand",
        "price_usd": "Price",
        "rating": "Rating",
        "reviews": "Reviews",
        "theme": "Main Abnormal Issue",
        "percent_of_reviews_product": "Product Issue %",
        "percent_of_reviews_baseline": "Baseline %",
        "lift": "Lift",
        "issue_strength": "Signal Strength"
    }
)

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True
)

st.subheader("Product Diagnostic")

product_options = filtered["product_name"].tolist()

selected_product = st.selectbox(
    "Select a product",
    product_options
)

selected_row = filtered[
    filtered["product_name"] == selected_product
].iloc[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Rating",
        f"{selected_row['rating']:.2f}"
    )

with col2:
    st.metric(
        "Reviews",
        f"{int(selected_row['reviews']):,}"
    )

with col3:
    st.metric(
        "Main Issue",
        selected_row["theme"].title()
    )

with col4:
    st.metric(
        "Complaint Lift",
        f"{selected_row['lift']:.1f}×"
    )

    st.write(
    f"**{selected_row['theme'].title()} complaints appear "
    f"{selected_row['lift']:.1f}× more often than the skincare baseline.**"
)

st.write(
    f"{selected_row['percent_of_reviews_product']:.1f}% of this product's "
    f"negative reviews mention this issue, compared with "
    f"{selected_row['percent_of_reviews_baseline']:.1f}% across skincare."
)

if selected_row["lift"] >= 5:
    takeaway = "This is a highly concentrated product-specific pain point."
elif selected_row["lift"] >= 3:
    takeaway = "This is a strong product-specific pain point."
elif selected_row["lift"] >= 2:
    takeaway = "This issue is meaningfully elevated compared with similar skincare feedback."
else:
    takeaway = "This issue is elevated, but the signal is less extreme."

st.info(takeaway)

selected_issues = all_diagnostics[
    all_diagnostics["product_name"] == selected_product
].sort_values(
    "lift",
    ascending=False
).head(3)

st.subheader("Key Elevated Issues")

for _, row in selected_issues.iterrows():
    st.write(
        f"**{row['theme'].title()}** — "
        f"{row['percent_of_reviews_product']:.1f}% of negative reviews "
        f"vs {row['percent_of_reviews_baseline']:.1f}% baseline "
        f"(**{row['lift']:.1f}× lift**)"
    )

st.subheader("Example Customer Reviews")

selected_theme = selected_row["theme"]

theme_keywords = complaint_themes[selected_theme]

pattern = "|".join(theme_keywords)

matching_reviews = reviews[
    (reviews["product_name"] == selected_product) &
    (reviews["rating"] <= 2) &
    (
        reviews["review_text"]
        .fillna("")
        .str.lower()
        .str.contains(pattern, regex=True, na=False)
    )
].copy()

matching_reviews = matching_reviews[
    ["rating", "review_text"]
].head(3)

if matching_reviews.empty:
    st.write("No matching review examples found.")
else:
    for _, review in matching_reviews.iterrows():
        st.markdown(
            f"**{int(review['rating'])}★ review**"
        )
        st.write(review["review_text"])
        st.divider()


st.subheader("AI Review Insights")

st.caption(
    "Uses AI to synthesize recurring themes from a sample of "
    "low-rated customer reviews for the selected product."
)

if st.button("Generate AI Insights"):

    with st.spinner("Analyzing customer reviews..."):

        ai_insights = generate_ai_insights(
            selected_product,
            reviews
        )

    st.write(ai_insights)