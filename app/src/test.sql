CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100) NOT NULL,
  is_active BOOLEAN
);

CREATE TABLE posts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  content TEXT,
  published_at DATETIME
);

CREATE TABLE connections (
  user_id INT PRIMARY KEY,
  friend_id INT PRIMARY KEY,
  connected_at DATETIME
);