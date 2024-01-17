-- Creates a DATABASE hbtn_0d_usa
-- Creates a table called states

CREATE DATABASE
       IF NOT EXISTS
       `hbtn_0d_usa`;

CREATE TABLE
       IF NOT EXISTS
       `hbtn_0d_usa`.`states`(
       `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
       `name` VARCHAR(256) NOT NULL);
