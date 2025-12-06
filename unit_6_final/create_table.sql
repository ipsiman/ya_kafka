CREATE TABLE IF NOT EXISTS purchases (
    order_id VARCHAR(255),
    customer_name VARCHAR(255),
    product_name VARCHAR(255),
    quantity INTEGER,
    amount DOUBLE PRECISION,
    timestamp BIGINT
);

INSERT INTO public.purchases (order_id, customer_name, product_name, quantity, amount, timestamp)
VALUES ('test', 'John Doe', 'Product 1', 1, 10.0, 1677609600000);

select from public.purchases;
