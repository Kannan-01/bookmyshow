-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 24, 2024 at 08:04 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `moviedatabase`
--

-- --------------------------------------------------------

--
-- Table structure for table `movies`
--

CREATE TABLE `movies` (
  `movie_id` int(11) NOT NULL,
  `movie_name` varchar(40) DEFAULT NULL,
  `length` int(11) DEFAULT NULL,
  `language` varchar(10) DEFAULT NULL,
  `format` varchar(10) DEFAULT NULL,
  `genre` varchar(40) DEFAULT NULL,
  `poster_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `movies`
--

INSERT INTO `movies` (`movie_id`, `movie_name`, `length`, `language`, `format`, `genre`, `poster_path`) VALUES
(314460280, 'Turbo', 168, 'Malayalam', ' 2D', 'Action/Comedy', 'uploads/CBRqel4Yzm8BS4fTMScYA1fQLD.jpg'),
(576056019, 'premalu', 156, 'Malayalam', ' 2D', 'Comedy/Romance', 'uploads/2eGRNxXn1idwPB1L3mzm84YVSCn.jpg'),
(722263035, 'The First Omen', 200, 'English', ' 2D', 'Horror', 'uploads/uGyiewQnDHPuiHN9V4k2t9QBPnh.jpg'),
(821068637, 'Aavesham', 167, 'Malayalam', ' 2D', 'Action/Comedy', 'uploads/pivTIbjNkJbtY5ELVEoIZH5n78w.jpg'),
(832765314, 'Fall Guy', 130, 'English', '3D', 'Action/Comedy', 'uploads/aBkqu7EddWK7qmY4grL4I6edx2h.jpg'),
(1119500571, 'Deadpool & Wolverine ', 220, 'English', 'IMAX', 'Action/Comedy', 'uploads/jbwYaoYWZwxtPP76AZnfYKQjCEB.jpg'),
(1413445711, 'Varshangalkku Shesham ', 150, 'Malayalam', ' 2D', 'Drama/Comedy', 'uploads/6VKnzX7JovRHHd1wlFhNeLG6ncY.jpg'),
(1827695656, 'Gaganachari ', 120, 'Malayalam', ' 2D', 'Science Fiction/Comedy', 'uploads/qTrGkS3Khx2Vj7Z3IplpiDqBkwv.jpg'),
(1848588691, 'Manjummel Boys', 220, 'Malayalam', ' 2D', 'Horror/survival', 'uploads/bswrtewwthpsh6nABiqKevU4UBI.jpg'),
(2045310631, 'Bramayugam', 170, 'Malayalam', ' 2D', 'Horror/Thriller', 'uploads/cm0eai2fyxM0IjZTLTlndoPo0HG.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `reservations`
--

CREATE TABLE `reservations` (
  `id` int(11) NOT NULL,
  `movie_id` int(11) DEFAULT NULL,
  `seat_row` varchar(2) DEFAULT NULL,
  `seat_number` int(11) DEFAULT NULL,
  `reservation_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `reservations`
--

INSERT INTO `reservations` (`id`, `movie_id`, `seat_row`, `seat_number`, `reservation_date`) VALUES
(1, 1119500571, 'E', 9, '2024-06-24'),
(2, 821068637, 'D', 9, '2024-06-23');

-- --------------------------------------------------------

--
-- Table structure for table `schedules`
--

CREATE TABLE `schedules` (
  `movie_id` int(11) NOT NULL,
  `time` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `schedules`
--

INSERT INTO `schedules` (`movie_id`, `time`) VALUES
(576056019, '09:20:00'),
(722263035, '11:00:00'),
(821068637, '10:20:00'),
(832765314, '07:30:00'),
(1119500571, '10:10:00'),
(1413445711, '02:30:00'),
(1827695656, '11:20:00'),
(1848588691, '11:35:00');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `movies`
--
ALTER TABLE `movies`
  ADD UNIQUE KEY `movie_id` (`movie_id`);

--
-- Indexes for table `reservations`
--
ALTER TABLE `reservations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `movie_id` (`movie_id`);

--
-- Indexes for table `schedules`
--
ALTER TABLE `schedules`
  ADD UNIQUE KEY `movie_id_2` (`movie_id`),
  ADD KEY `movie_id` (`movie_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `reservations`
--
ALTER TABLE `reservations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `reservations`
--
ALTER TABLE `reservations`
  ADD CONSTRAINT `reservations_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`movie_id`);

--
-- Constraints for table `schedules`
--
ALTER TABLE `schedules`
  ADD CONSTRAINT `movieId` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`movie_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
