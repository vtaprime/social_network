-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema social_sharing
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema social_sharing
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `social_sharing` DEFAULT CHARACTER SET utf8 ;
USE `social_sharing` ;

-- -----------------------------------------------------
-- Table `social_sharing`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `social_sharing`.`user` (
  `user_id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) CHARACTER SET 'big5' NOT NULL,
  `age` INT(11) NULL DEFAULT NULL,
  `gender` VARCHAR(10) CHARACTER SET 'big5' NULL DEFAULT NULL,
  `is_super_user` INT(1) NOT NULL,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`user_id`))
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `social_sharing`.`event`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `social_sharing`.`event` (
  `event_id` INT(11) NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(200) NOT NULL,
  `description` TEXT NOT NULL,
  `photo` TEXT NULL DEFAULT NULL,
  `date` VARCHAR(45) NOT NULL,
  `location` VARCHAR(200) NULL DEFAULT NULL,
  `participant` TEXT NULL DEFAULT NULL,
  `user_id` INT(11) NOT NULL,
  PRIMARY KEY (`event_id`),
  INDEX `USER_OF_EVENT_idx` (`user_id` ASC),
  CONSTRAINT `USER_OF_EVENT`
    FOREIGN KEY (`user_id`)
    REFERENCES `social_sharing`.`user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `social_sharing`.`comment`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `social_sharing`.`comment` (
  `comment_id` INT(11) NOT NULL AUTO_INCREMENT,
  `content` TEXT NOT NULL,
  `event_id` INT(11) NOT NULL,
  `user_id` INT(11) NOT NULL,
  PRIMARY KEY (`comment_id`),
  INDEX `USER_OF_COMMENT_idx` (`user_id` ASC),
  INDEX `EVENT_OF_COMMENT_idx` (`event_id` ASC),
  CONSTRAINT `EVENT_OF_COMMENT`
    FOREIGN KEY (`event_id`)
    REFERENCES `social_sharing`.`event` (`event_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `USER_OF_COMMENT`
    FOREIGN KEY (`user_id`)
    REFERENCES `social_sharing`.`user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `social_sharing`.`django_content_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `social_sharing`.`django_content_type` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `app_label` VARCHAR(100) NOT NULL,
  `model` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label` ASC, `model` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `social_sharing`.`django_migrations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `social_sharing`.`django_migrations` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `app` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `applied` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `social_sharing`.`reaction`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `social_sharing`.`reaction` (
  `reactionid` INT(11) NOT NULL AUTO_INCREMENT,
  `like_number` INT(11) NOT NULL,
  `user_like` TEXT NOT NULL,
  `event_id` INT(11) NOT NULL,
  PRIMARY KEY (`reactionid`),
  INDEX `REACTION_OF_EVENT_idx` (`event_id` ASC),
  CONSTRAINT `REACTION_OF_EVENT`
    FOREIGN KEY (`event_id`)
    REFERENCES `social_sharing`.`event` (`event_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
