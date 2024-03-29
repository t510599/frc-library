-- MySQL Script generated by MySQL Workbench
-- Tue Jul  2 14:32:57 2019
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema frc_library
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema frc_library
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `frc_library` DEFAULT CHARACTER SET utf8 ;
USE `frc_library` ;

-- -----------------------------------------------------
-- Table `frc_library`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `frc_library`.`user` (
  `username` VARCHAR(16) NOT NULL UNIQUE,
  `user_id` INT(10) NOT NULL,
  `encoding` TEXT NOT NULL,
  PRIMARY KEY (`user_id`));

-- -----------------------------------------------------
-- Table `frc_library`.`books`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `frc_library`.`books` (
  `book_id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `lent` TINYINT(1) NOT NULL DEFAULT 0,
  `borrower_id` INT(10) NULL,
  `time` TIMESTAMP NULL,
  PRIMARY KEY (`book_id`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
