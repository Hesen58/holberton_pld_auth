CREATE DATABASE if not exists book_management;
CREATE USER  if not exists'book'@'localhost' IDENTIFIED BY 'hoqqa';
GRANT ALL PRIVILEGES ON book_management.* TO 'book'@'localhost';
