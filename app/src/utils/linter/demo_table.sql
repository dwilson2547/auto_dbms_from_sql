CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT
     NULL,
    price DECIMAL(10, 2),
    category_id INT
    ,
    description TEXT
    ,,
    created_date TIMESTAMP DEFAULT
    CURRENT_TIMESTAMP
);
