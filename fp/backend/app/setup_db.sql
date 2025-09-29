CREATE DATABASE IF NOT EXISTS `OnlyFood` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `OnlyFood`;

-- Create the `role` table
CREATE TABLE IF NOT EXISTS `role` (
  `id_role` INT NOT NULL AUTO_INCREMENT,
  `description` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id_role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create the `user` table
CREATE TABLE IF NOT EXISTS `user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `lastname` VARCHAR(100) NOT NULL,
  `id_role` INT NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_role`) REFERENCES `role` (`id_role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create the `posts` table
CREATE TABLE IF NOT EXISTS `posts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Insert default roles
INSERT IGNORE INTO `role` (`id_role`, `description`) VALUES
(1, 'Admin'),
(2, 'User');

-- Insert default users
INSERT IGNORE INTO `user` (`id`, `name`, `lastname`, `id_role`, `password`) VALUES
(1, 'John', 'Doe', 1, 'admin123'),
(2, 'Jane', 'Smith', 2, 'user123');

-- Create the stored procedure for user authentication
CREATE PROCEDURE `sp_login_user`(
    IN p_name VARCHAR(255),
    IN p_lastname VARCHAR(255),
    IN p_password VARCHAR(255)
)
BEGIN
    SELECT * 
    FROM `user`
    WHERE `name` = p_name 
    AND `lastname` = p_lastname 
    AND `password` = p_password;
END;

CREATE TABLE IF NOT EXISTS user_profile (
  user_id INT NOT NULL PRIMARY KEY,
  bio VARCHAR(500),
  location VARCHAR(100),
  avatar_url VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user(id)
);