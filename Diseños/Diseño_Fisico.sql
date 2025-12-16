-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `mydb` ;

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`Dim_Tiempo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Dim_Tiempo` (
  `id_tiempo` INT NOT NULL AUTO_INCREMENT,
  `anyo` INT NULL,
  `mes` INT NULL,
  `dia` INT NULL,
  `hora` INT NULL,
  `franja_horaria` VARCHAR(45) NULL,
  `tipo_dia` VARCHAR(45) NULL,
  PRIMARY KEY (`id_tiempo`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Dim_Tipo_Accidente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Dim_Tipo_Accidente` (
  `id_tipo_accidente` INT NOT NULL AUTO_INCREMENT,
  `tipo_accidente` VARCHAR(70) NULL,
  PRIMARY KEY (`id_tipo_accidente`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Dim_Prioridad_senalizacion`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Dim_Prioridad_senalizacion` (
  `id_prioridad_senalizacion` INT NOT NULL AUTO_INCREMENT,
  `priori_agente` VARCHAR(45) NULL,
  `priori_circunstancial` VARCHAR(45) NULL,
  `priori_horiz_ceda` VARCHAR(45) NULL,
  `priori_horiz_stop` VARCHAR(45) NULL,
  `priori_semaforo` VARCHAR(45) NULL,
  `priori_vert_ceda` VARCHAR(45) NULL,
  `priori_vert_stop` VARCHAR(45) NULL,
  PRIMARY KEY (`id_prioridad_senalizacion`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Dim_Clima`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Dim_Clima` (
  `id_clima` INT NOT NULL AUTO_INCREMENT,
  `condicion_firme` VARCHAR(45) NULL,
  `condicion_iluminacion` VARCHAR(45) NULL,
  `condicion_meteo` VARCHAR(45) NULL,
  `condicion_niebla` VARCHAR(45) NULL,
  `condicion_nivel_circula` VARCHAR(45) NULL,
  `condicion_viento` VARCHAR(45) NULL,
  PRIMARY KEY (`id_clima`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Dim_Ubicacion`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Dim_Ubicacion` (
  `id_ubicacion` INT NOT NULL AUTO_INCREMENT,
  `cod_municipio` INT NULL,
  `zona` VARCHAR(45) NULL,
  `trazado_planta` VARCHAR(45) NULL,
  PRIMARY KEY (`id_ubicacion`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Dim_Via`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Dim_Via` (
  `id_via` INT NOT NULL AUTO_INCREMENT,
  `carretera` VARCHAR(45) NULL,
  `carretera_cruce` VARCHAR(45) NULL,
  `sentido_1f` VARCHAR(45) NULL,
  `tipo_via` VARCHAR(70) NULL,
  `titularidad_via` VARCHAR(45) NULL,
  PRIMARY KEY (`id_via`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Hecho_Accidente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Hecho_Accidente` (
  `id_hecho_accidente` INT NOT NULL AUTO_INCREMENT,
  `id_accidente` INT NULL,
  `km` DECIMAL(3) NULL,
  `total_hg24h` INT NULL,
  `total_hl24h` INT NULL,
  `total_mu24h` INT NULL,
  `id_tiempo` INT NOT NULL,
  `id_tipo_accidente` INT NOT NULL,
  `id_prioridad_senalizacion` INT NOT NULL,
  `id_clima` INT NOT NULL,
  `id_ubicacion` INT NOT NULL,
  `id_via` INT NOT NULL,
  PRIMARY KEY (`id_hecho_accidente`),
  INDEX `id_tiempo_idx` (`id_tiempo` ASC) VISIBLE,
  INDEX `id_tipo_accidente_idx` (`id_tipo_accidente` ASC) VISIBLE,
  INDEX `id_prioridad_senalizacion_idx` (`id_prioridad_senalizacion` ASC) VISIBLE,
  INDEX `id_clima_idx` (`id_clima` ASC) VISIBLE,
  INDEX `id_ubicacion_idx` (`id_ubicacion` ASC) VISIBLE,
  INDEX `id_via_idx` (`id_via` ASC) VISIBLE,
  CONSTRAINT `id_tiempo`
    FOREIGN KEY (`id_tiempo`)
    REFERENCES `mydb`.`Dim_Tiempo` (`id_tiempo`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `id_tipo_accidente`
    FOREIGN KEY (`id_tipo_accidente`)
    REFERENCES `mydb`.`Dim_Tipo_Accidente` (`id_tipo_accidente`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `id_prioridad_senalizacion`
    FOREIGN KEY (`id_prioridad_senalizacion`)
    REFERENCES `mydb`.`Dim_Prioridad_senalizacion` (`id_prioridad_senalizacion`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `id_clima`
    FOREIGN KEY (`id_clima`)
    REFERENCES `mydb`.`Dim_Clima` (`id_clima`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `id_ubicacion`
    FOREIGN KEY (`id_ubicacion`)
    REFERENCES `mydb`.`Dim_Ubicacion` (`id_ubicacion`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `id_via`
    FOREIGN KEY (`id_via`)
    REFERENCES `mydb`.`Dim_Via` (`id_via`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
