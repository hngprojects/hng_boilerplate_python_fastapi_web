-- Creates a database hbtn_0d_2 if not exists
-- Creates a User user_0d_2 if not exists

CREATE DATABASE
       IF NOT EXISTS `hbtn_0d_2`;

CREATE USER
       IF NOT EXISTS 'user_0d_2'@'localhost'
       IDENTIFIED BY 'user_0d_2_pwd';

GRANT SELECT
      ON `hbtn_0d_2`.*
      TO 'user_0d_2'@'localhost';
