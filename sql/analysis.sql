-- BeautyIQ SQL Analysis
-- Business-focused analysis of Sephora product and skincare review data

-- 1. Average rating and price by primary category

SELECT
    primary_category,
    COUNT(*) AS product_count,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(AVG(price_usd), 2) AS avg_price
FROM products
WHERE rating IS NOT NULL
GROUP BY primary_category
ORDER BY avg_rating DESC;


-- 2. Strongest customer interest by brand
-- Only include brands with at least 10 products to avoid tiny samples

SELECT
    brand_name,
    COUNT(*) AS product_count,
    SUM(loves_count) AS total_loves,
    ROUND(AVG(loves_count), 0) AS avg_loves_per_product,
    ROUND(AVG(rating), 2) AS avg_rating
FROM products
WHERE rating IS NOT NULL
GROUP BY brand_name
HAVING COUNT(*) >= 10
ORDER BY total_loves DESC
LIMIT 15;

-- 3. High-interest products with relatively weak ratings
-- Potential product improvement opportunities

SELECT
    product_name,
    brand_name,
    primary_category,
    loves_count,
    reviews,
    ROUND(rating, 2) AS rating,
    ROUND(price_usd, 2) AS price_usd
FROM products
WHERE rating IS NOT NULL
  AND loves_count >= 10000
  AND rating < 4.0
ORDER BY loves_count DESC
LIMIT 20;

-- 4. High-interest skincare products with weaker ratings
-- These can later be investigated using customer review text

SELECT
    product_id,
    product_name,
    brand_name,
    loves_count,
    reviews,
    ROUND(rating, 2) AS rating,
    ROUND(price_usd, 2) AS price_usd
FROM products
WHERE primary_category = 'Skincare'
  AND rating IS NOT NULL
  AND loves_count >= 10000
  AND rating < 4.0
ORDER BY loves_count DESC
LIMIT 20;

-- 5. Skincare brands with the highest review activity

SELECT
    brand_name,
    COUNT(*) AS review_count,
    COUNT(DISTINCT product_id) AS reviewed_products,
    ROUND(AVG(rating), 2) AS avg_review_rating
FROM reviews
GROUP BY brand_name
ORDER BY review_count DESC
LIMIT 15;