-- MySQL dump 10.13  Distrib 5.5.57, for debian-linux-gnu (x86_64)
--
-- Host: 0.0.0.0    Database: c9
-- ------------------------------------------------------
-- Server version	5.5.57-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `isReported`
--

DROP TABLE IF EXISTS `isReported`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `isReported` (
  `pid` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  PRIMARY KEY (`pid`,`username`),
  KEY `username` (`username`),
  CONSTRAINT `isReported_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`) ON UPDATE CASCADE,
  CONSTRAINT `isReported_ibfk_2` FOREIGN KEY (`username`) REFERENCES `accounts` (`username`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `isReported`
--

LOCK TABLES `isReported` WRITE;
/*!40000 ALTER TABLE `isReported` DISABLE KEYS */;
/*!40000 ALTER TABLE `isReported` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tagged`
--

DROP TABLE IF EXISTS `tagged`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tagged` (
  `tid` int(11) NOT NULL,
  `pid` int(11) NOT NULL,
  PRIMARY KEY (`tid`,`pid`),
  KEY `pid` (`pid`),
  CONSTRAINT `tagged_ibfk_1` FOREIGN KEY (`tid`) REFERENCES `tags` (`tid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tagged_ibfk_2` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tagged`
--

LOCK TABLES `tagged` WRITE;
/*!40000 ALTER TABLE `tagged` DISABLE KEYS */;
INSERT INTO `tagged` VALUES (1,10),(1,11),(7,12),(7,13),(8,14),(9,15),(10,15),(11,15),(8,16),(1,17),(12,17);
/*!40000 ALTER TABLE `tagged` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `starred`
--

DROP TABLE IF EXISTS `starred`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `starred` (
  `pid` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  PRIMARY KEY (`pid`,`username`),
  KEY `username` (`username`),
  CONSTRAINT `starred_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`) ON UPDATE CASCADE,
  CONSTRAINT `starred_ibfk_2` FOREIGN KEY (`username`) REFERENCES `accounts` (`username`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `starred`
--

LOCK TABLES `starred` WRITE;
/*!40000 ALTER TABLE `starred` DISABLE KEYS */;
/*!40000 ALTER TABLE `starred` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posted`
--

DROP TABLE IF EXISTS `posted`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `posted` (
  `pid` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  PRIMARY KEY (`pid`,`username`),
  KEY `username` (`username`),
  CONSTRAINT `posted_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`) ON UPDATE CASCADE,
  CONSTRAINT `posted_ibfk_2` FOREIGN KEY (`username`) REFERENCES `accounts` (`username`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posted`
--

LOCK TABLES `posted` WRITE;
/*!40000 ALTER TABLE `posted` DISABLE KEYS */;
/*!40000 ALTER TABLE `posted` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `followed`
--

DROP TABLE IF EXISTS `followed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `followed` (
  `tid` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  PRIMARY KEY (`tid`,`username`),
  KEY `username` (`username`),
  CONSTRAINT `followed_ibfk_1` FOREIGN KEY (`tid`) REFERENCES `tags` (`tid`) ON UPDATE CASCADE,
  CONSTRAINT `followed_ibfk_2` FOREIGN KEY (`username`) REFERENCES `accounts` (`username`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `followed`
--

LOCK TABLES `followed` WRITE;
/*!40000 ALTER TABLE `followed` DISABLE KEYS */;
/*!40000 ALTER TABLE `followed` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts` (
  `username` varchar(30) NOT NULL,
  `hashed` varchar(60) DEFAULT NULL,
  `isAdmin` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES ('scott','$2b$12$Rufx46Wl0Qh7/BiCCHHIvOrMl59fxBecgc3lZWoilIRZb6Qa47PR.',NULL),('shrunothra','$2b$12$EiBTvW7A4NGWeVfihY0BXO6tf8DxIvl6AHpBUPg6xgmOF2SKArWt2',NULL),('wendy','$2b$12$ictIt4WXq24OGfyWfkrb1udq1PFnlviFqURakA0kMyaPx3yo8Ykvm',NULL);
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts`
--

DROP TABLE IF EXISTS `posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `posts` (
  `pid` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(60) NOT NULL,
  `content` varchar(1000) DEFAULT NULL,
  `time_created` datetime DEFAULT NULL,
  `location` varchar(60) DEFAULT NULL,
  `num_starred` int(10) unsigned DEFAULT NULL,
  `imagefile` varchar(60) DEFAULT NULL,
  `event_time` time NOT NULL,
  `event_date` date NOT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts`
--

LOCK TABLES `posts` WRITE;
/*!40000 ALTER TABLE `posts` DISABLE KEYS */;
INSERT INTO `posts` VALUES (1,'firstpost',' this is the first post','0000-00-00 00:00:00',' Tower Great Hall',0,' NULL','05:55:00','2019-04-15'),(10,'testing_tags','testing on tags!','2019-04-19 03:21:51','tower',0,NULL,'23:21:00','2019-04-18'),(11,'testing on tags again','on tags','2019-04-19 03:25:31','tower',0,NULL,'23:25:00','2019-04-18'),(12,'final testing on tags','im going to sleep bye','2019-04-19 03:27:43','tower',0,NULL,'23:27:00','2019-04-18'),(13,'final test on tags v2','oops','2019-04-19 03:29:30','tower',0,NULL,'23:29:00','2019-04-18'),(14,'bad event','This is <em>very</em> interesting','2019-04-19 21:08:29','tower',0,NULL,'17:08:00','2019-04-19'),(15,'shrunothra\'s birthday party','my 21st bdayyy','2019-04-19 21:23:53','Wellesley',0,NULL,'22:10:00','2019-05-24'),(16,'bad post','This is terrible. <script>window.location=\'https://www.youtube.com/watch?reload=9&v=dQw4w9WgXcQ\';</script>','2019-04-20 03:14:56','terrible',0,NULL,'23:14:00','2019-04-19'),(17,'TEA','tea with cs faculty','2019-04-24 18:17:04','micro-focus',0,NULL,'16:30:00','2019-04-25');
/*!40000 ALTER TABLE `posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tags` (
  `tid` int(11) NOT NULL AUTO_INCREMENT,
  `tag_name` varchar(100) DEFAULT NULL,
  `num_followers` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`tid`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES (1,'cs',3),(2,'wasac',50),(3,'chocolate',100),(4,'test1',NULL),(5,'test2',NULL),(6,'',NULL),(7,'testing3',NULL),(8,'bad',NULL),(9,'birthday',NULL),(10,'party',NULL),(11,'drinks',NULL),(12,' tea',NULL);
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-05-05 20:18:12
