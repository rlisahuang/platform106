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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES (1,'cs',3),(2,'wasac',50),(3,'chocolate',100);
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
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
  `date_created` date DEFAULT NULL,
  `location` varchar(60) DEFAULT NULL,
  `num_starred` int(10) unsigned DEFAULT NULL,
  `imagefile` varchar(60) DEFAULT NULL,
  `event_date` date NOT NULL,
  `event_time` time DEFAULT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts`
--

LOCK TABLES `posts` WRITE;
/*!40000 ALTER TABLE `posts` DISABLE KEYS */;
INSERT INTO `posts` VALUES (1,'firstpost',' this is the first post','2019-04-13',' Tower Great Hall',0,' NULL','0000-00-00',NULL),(2,'tesing!','just for fun','0000-00-00','sci s173',0,NULL,'2019-04-17',NULL),(3,'testing2','haha','0000-00-00','sci s173',0,NULL,'2019-04-17',NULL),(4,'tesing3','testing again','0000-00-00','sci e111',0,NULL,'2019-04-17',NULL),(5,'testing5','hi','0000-00-00','sci',0,NULL,'2019-04-17',NULL),(6,'hi','123','0000-00-00','456',0,NULL,'0000-00-00',NULL),(7,'hi','123','0000-00-00','456',0,NULL,'0000-00-00',NULL),(8,'hi','123','0000-00-00','456',0,NULL,'0000-00-00',NULL),(9,'hi','123','0000-00-00','456',0,NULL,'0000-00-00',NULL),(10,'hello','not fun','0000-00-00','tower',0,NULL,'2019-04-18',NULL),(11,'secondpost','our second post!','0000-00-00','Wellesley',0,NULL,'2019-04-19',NULL),(12,'tesing!','testing','0000-00-00','tower',0,NULL,'2019-04-18',NULL),(13,'testing123','testingfrompython','0000-00-00','tower',0,NULL,'2019-04-18',NULL),(14,'testing123','testingfrompython','0000-00-00','tower',0,NULL,'2019-04-18',NULL),(15,'tesing!','testing','0000-00-00','tower',0,NULL,'2019-04-18',NULL),(16,'some other testing','testing again','0000-00-00','tower',0,NULL,'2019-04-18',NULL),(17,'testing on event time','123','0000-00-00','tower',0,NULL,'2019-04-18','17:55:00'),(18,'testing_date_created','testingfrompython','0000-00-00','tower',0,NULL,'2019-04-18','05:55:00'),(19,'testing_date_created','testingfrompython','0000-00-00','tower',0,NULL,'2019-04-18','05:55:00'),(20,'testing_date_created','testingfrompython','0000-00-00','tower',0,NULL,'2019-04-18','05:55:00');
/*!40000 ALTER TABLE `posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) DEFAULT NULL,
  `isAdmin` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES (1,'sambati',0),(2,'rhuang2',0),(3,'jshiue',1);
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `followed`
--

DROP TABLE IF EXISTS `followed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `followed` (
  `tid` int(11) NOT NULL,
  `uid` int(11) NOT NULL,
  PRIMARY KEY (`tid`,`uid`),
  KEY `uid` (`uid`),
  CONSTRAINT `followed_ibfk_1` FOREIGN KEY (`tid`) REFERENCES `tags` (`tid`) ON UPDATE CASCADE,
  CONSTRAINT `followed_ibfk_2` FOREIGN KEY (`uid`) REFERENCES `accounts` (`uid`) ON UPDATE CASCADE
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
-- Table structure for table `posted`
--

DROP TABLE IF EXISTS `posted`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `posted` (
  `pid` int(11) NOT NULL,
  `uid` int(11) NOT NULL,
  PRIMARY KEY (`pid`,`uid`),
  KEY `uid` (`uid`),
  CONSTRAINT `posted_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`) ON UPDATE CASCADE,
  CONSTRAINT `posted_ibfk_2` FOREIGN KEY (`uid`) REFERENCES `accounts` (`uid`) ON UPDATE CASCADE
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
-- Table structure for table `starred`
--

DROP TABLE IF EXISTS `starred`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `starred` (
  `pid` int(11) NOT NULL,
  `uid` int(11) NOT NULL,
  PRIMARY KEY (`pid`,`uid`),
  KEY `uid` (`uid`),
  CONSTRAINT `starred_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`) ON UPDATE CASCADE,
  CONSTRAINT `starred_ibfk_2` FOREIGN KEY (`uid`) REFERENCES `accounts` (`uid`) ON UPDATE CASCADE
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
/*!40000 ALTER TABLE `tagged` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `isReported`
--

DROP TABLE IF EXISTS `isReported`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `isReported` (
  `pid` int(11) NOT NULL,
  `uid` int(11) NOT NULL,
  PRIMARY KEY (`pid`,`uid`),
  KEY `uid` (`uid`),
  CONSTRAINT `isReported_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`) ON UPDATE CASCADE,
  CONSTRAINT `isReported_ibfk_2` FOREIGN KEY (`uid`) REFERENCES `accounts` (`uid`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `isReported`
--

LOCK TABLES `isReported` WRITE;
/*!40000 ALTER TABLE `isReported` DISABLE KEYS */;
/*!40000 ALTER TABLE `isReported` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-04-18 20:25:47
