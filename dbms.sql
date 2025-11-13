-- Dumped by Event Management App
-- Auto-generated on: 2025-11-11 10:16:39
DROP DATABASE IF EXISTS Event_Management_DB;
CREATE DATABASE Event_Management_DB;
USE Event_Management_DB;


-- Table structure for organizer
CREATE TABLE `organizer` (
  `Organizer_id` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Contact` varchar(15) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Organizer_id`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Table structure for venue
CREATE TABLE `venue` (
  `Venue_id` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Location` varchar(255) DEFAULT NULL,
  `Capacity` int DEFAULT NULL,
  PRIMARY KEY (`Venue_id`),
  CONSTRAINT `venue_chk_1` CHECK ((`Capacity` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Table structure for event
CREATE TABLE `event` (
  `Event_id` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Type` varchar(50) DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `Time` time DEFAULT NULL,
  `Venue_id` int NOT NULL,
  `Organizer_id` int NOT NULL,
  PRIMARY KEY (`Event_id`),
  KEY `Venue_id` (`Venue_id`),
  KEY `Organizer_id` (`Organizer_id`),
  CONSTRAINT `event_ibfk_1` FOREIGN KEY (`Venue_id`) REFERENCES `venue` (`Venue_id`),
  CONSTRAINT `event_ibfk_2` FOREIGN KEY (`Organizer_id`) REFERENCES `organizer` (`Organizer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Table structure for participants
CREATE TABLE `participants` (
  `Participant_id` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `Contact` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`Participant_id`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Table structure for ticket
CREATE TABLE `ticket` (
  `Ticket_id` int NOT NULL,
  `Event_id` int NOT NULL,
  `Participant_id` int NOT NULL,
  `Status` varchar(50) DEFAULT 'Pending',
  `Price` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`Ticket_id`),
  KEY `Event_id` (`Event_id`),
  KEY `Participant_id` (`Participant_id`),
  CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`Event_id`) REFERENCES `event` (`Event_id`),
  CONSTRAINT `ticket_ibfk_2` FOREIGN KEY (`Participant_id`) REFERENCES `participants` (`Participant_id`),
  CONSTRAINT `ticket_chk_1` CHECK ((`Status` in (_utf8mb4'Confirmed',_utf8mb4'Pending',_utf8mb4'Cancelled'))),
  CONSTRAINT `ticket_chk_2` CHECK ((`Price` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Table structure for payment
CREATE TABLE `payment` (
  `Payment_id` int NOT NULL AUTO_INCREMENT,
  `Ticket_id` int NOT NULL,
  `Amount` decimal(10,2) NOT NULL,
  `Method` varchar(50) DEFAULT NULL,
  `Date` date DEFAULT NULL,
  PRIMARY KEY (`Payment_id`),
  UNIQUE KEY `Ticket_id` (`Ticket_id`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`Ticket_id`) REFERENCES `ticket` (`Ticket_id`),
  CONSTRAINT `payment_chk_1` CHECK ((`Amount` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Table structure for sponsor
CREATE TABLE `sponsor` (
  `Sponsor_id` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Event_id` int NOT NULL,
  `Contribution` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`Sponsor_id`),
  KEY `Event_id` (`Event_id`),
  CONSTRAINT `sponsor_ibfk_1` FOREIGN KEY (`Event_id`) REFERENCES `event` (`Event_id`),
  CONSTRAINT `sponsor_chk_1` CHECK ((`Contribution` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Table structure for volunteers
CREATE TABLE `volunteers` (
  `Volunteer_id` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `Contact` varchar(15) DEFAULT NULL,
  `Type` varchar(50) DEFAULT NULL,
  `Event_id` int NOT NULL,
  PRIMARY KEY (`Volunteer_id`),
  UNIQUE KEY `Email` (`Email`),
  KEY `Event_id` (`Event_id`),
  CONSTRAINT `volunteers_ibfk_1` FOREIGN KEY (`Event_id`) REFERENCES `event` (`Event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Table structure for log
CREATE TABLE `log` (
  `Log_id` int NOT NULL AUTO_INCREMENT,
  `Log_Message` text,
  `Timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Log_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Dumping data for table organizer
INSERT INTO `organizer` (`Organizer_id`, `Name`, `Contact`, `Email`) VALUES (1, 'Tech Summit Team', '9876543210', 'techsummit@org.com');
INSERT INTO `organizer` (`Organizer_id`, `Name`, `Contact`, `Email`) VALUES (2, 'Arts & Culture Co.', '8001122334', 'arts@org.com');
INSERT INTO `organizer` (`Organizer_id`, `Name`, `Contact`, `Email`) VALUES (3, 'Sports League PES', '7776665554', 'sports@pes.com');
INSERT INTO `organizer` (`Organizer_id`, `Name`, `Contact`, `Email`) VALUES (4, 'Alumni Network', '9998887776', 'alumni@pes.com');
INSERT INTO `organizer` (`Organizer_id`, `Name`, `Contact`, `Email`) VALUES (5, 'Student Council', '6004002001', 'council@pes.com');

-- Table structure for users (public/login accounts)
CREATE TABLE `users` (
    `User_id` int NOT NULL,
    `Username` varchar(50) NOT NULL,
    `Password` varchar(255) NOT NULL,
    `Fullname` varchar(100) DEFAULT NULL,
    `Email` varchar(100) DEFAULT NULL,
    `Role` varchar(20) DEFAULT 'user',
    PRIMARY KEY (`User_id`),
    UNIQUE KEY `Username` (`Username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Sample public user
INSERT INTO `users` (`User_id`, `Username`, `Password`, `Fullname`, `Email`, `Role`) VALUES (1, 'guest', 'guest', 'Guest User', 'guest@example.com', 'user');

-- Dumping data for table venue
INSERT INTO `venue` (`Venue_id`, `Name`, `Location`, `Capacity`) VALUES (10, 'Seminar Hall', 'PES Campus, BE Block', 500);
INSERT INTO `venue` (`Venue_id`, `Name`, `Location`, `Capacity`) VALUES (11, 'Auditorium', 'PES RR Campus', 150);
INSERT INTO `venue` (`Venue_id`, `Name`, `Location`, `Capacity`) VALUES (12, 'Football Ground', 'PES Main Field', 1000);
INSERT INTO `venue` (`Venue_id`, `Name`, `Location`, `Capacity`) VALUES (13, 'Library Discussion Room', 'Central Library, 2nd Floor', 50);
INSERT INTO `venue` (`Venue_id`, `Name`, `Location`, `Capacity`) VALUES (14, 'Quadrangle', 'Golden Jubilee Block', 300);
INSERT INTO `venue` (`Venue_id`, `Name`, `Location`, `Capacity`) VALUES (15, 'abc', 'canteen', 200);
INSERT INTO `venue` (`Venue_id`, `Name`, `Location`, `Capacity`) VALUES (16, 'aks', 'backgate', 1);

-- Dumping data for table event
INSERT INTO `event` (`Event_id`, `Name`, `Type`, `Date`, `Time`, `Venue_id`, `Organizer_id`) VALUES (101, 'EncodeAI Hackathon 3.0', 'Hackathon', '2025-10-20', '9:00:00', 10, 1);
INSERT INTO `event` (`Event_id`, `Name`, `Type`, `Date`, `Time`, `Venue_id`, `Organizer_id`) VALUES (102, 'Campus Treasure Hunt', 'Fun Activity', '2025-11-05', '14:00:00', 12, 3);
INSERT INTO `event` (`Event_id`, `Name`, `Type`, `Date`, `Time`, `Venue_id`, `Organizer_id`) VALUES (103, 'Resume Building Workshop', 'Workshop', '2025-11-15', '10:30:00', 13, 4);
INSERT INTO `event` (`Event_id`, `Name`, `Type`, `Date`, `Time`, `Venue_id`, `Organizer_id`) VALUES (104, 'DJ Night', 'Party', '2025-12-01', '19:00:00', 14, 5);
INSERT INTO `event` (`Event_id`, `Name`, `Type`, `Date`, `Time`, `Venue_id`, `Organizer_id`) VALUES (105, 'Future of AI Guest Lecture', 'Guest Lecture', '2025-10-28', '16:00:00', 11, 1);
INSERT INTO `event` (`Event_id`, `Name`, `Type`, `Date`, `Time`, `Venue_id`, `Organizer_id`) VALUES (110, 'sowk', 'Hackathon', '2025-11-07', '0:00:00', 13, 5);

-- Dumping data for table participants
INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) VALUES (1001, 'Ananya Sharma', 'ananya.s@email.com', '9876543210');
INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) VALUES (1002, 'Rohan Kapoor', 'rohan.k@email.com', '9988776655');
INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) VALUES (1003, 'Priya Singh', 'priya.s@email.com', '9001122334');
INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) VALUES (1004, 'Vihaan Reddy', 'vihaan.r@email.com', '8877665544');
INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) VALUES (1005, 'Kavya Menon', 'kavya.m@email.com', '7766554433');
INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) VALUES (1006, 'Aarav Patel', 'aarav.p@email.com', '9123456789');
INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) VALUES (1007, 'saaj shah', 'saaj@gmail.com', '7894561230');
INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) VALUES (1008, 'sathvik', 'sathvik@gmail.com', '8123891888');
INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) VALUES (1009, 'arham :)', 'arham@gmail.com', '9874561230');
INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) VALUES (1010, 'mohith', 'kulla@gmail.com', '8459631235');
INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) VALUES (1011, 'sankalp', 'sankalp@gmail.com', '9874563210');

-- Dumping data for table ticket
INSERT INTO `ticket` (`Ticket_id`, `Event_id`, `Participant_id`, `Status`, `Price`) VALUES (3001, 101, 1001, 'Confirmed', 500.00);
INSERT INTO `ticket` (`Ticket_id`, `Event_id`, `Participant_id`, `Status`, `Price`) VALUES (3002, 101, 1002, 'Pending', 500.00);
INSERT INTO `ticket` (`Ticket_id`, `Event_id`, `Participant_id`, `Status`, `Price`) VALUES (3003, 102, 1003, 'Pending', 100.00);
INSERT INTO `ticket` (`Ticket_id`, `Event_id`, `Participant_id`, `Status`, `Price`) VALUES (3004, 104, 1004, 'Pending', 50.00);
INSERT INTO `ticket` (`Ticket_id`, `Event_id`, `Participant_id`, `Status`, `Price`) VALUES (3005, 101, 1005, 'Confirmed', 500.00);
INSERT INTO `ticket` (`Ticket_id`, `Event_id`, `Participant_id`, `Status`, `Price`) VALUES (3006, 102, 1006, 'Cancelled', 100.00);
INSERT INTO `ticket` (`Ticket_id`, `Event_id`, `Participant_id`, `Status`, `Price`) VALUES (3007, 105, 1009, 'Confirmed', 500.00);

-- Dumping data for table payment
INSERT INTO `payment` (`Payment_id`, `Ticket_id`, `Amount`, `Method`, `Date`) VALUES (1, 3001, 500.00, 'Credit Card', '2025-08-01');
INSERT INTO `payment` (`Payment_id`, `Ticket_id`, `Amount`, `Method`, `Date`) VALUES (2, 3002, 500.00, 'UPI', '2025-08-05');
INSERT INTO `payment` (`Payment_id`, `Ticket_id`, `Amount`, `Method`, `Date`) VALUES (3, 3004, 50.00, 'Wallet', '2025-09-10');
INSERT INTO `payment` (`Payment_id`, `Ticket_id`, `Amount`, `Method`, `Date`) VALUES (4, 3005, 500.00, 'Debit Card', '2025-09-15');
INSERT INTO `payment` (`Payment_id`, `Ticket_id`, `Amount`, `Method`, `Date`) VALUES (5, 3007, 500.00, 'UPI', '2025-11-07');

-- Dumping data for table sponsor
INSERT INTO `sponsor` (`Sponsor_id`, `Name`, `Event_id`, `Contribution`) VALUES (50, 'Global Tech Inc.', 101, 50000.00);
INSERT INTO `sponsor` (`Sponsor_id`, `Name`, `Event_id`, `Contribution`) VALUES (51, 'Local Bank PES', 103, 10000.00);
INSERT INTO `sponsor` (`Sponsor_id`, `Name`, `Event_id`, `Contribution`) VALUES (52, 'Food Chain Delights', 105, 5000.00);
INSERT INTO `sponsor` (`Sponsor_id`, `Name`, `Event_id`, `Contribution`) VALUES (53, 'Software Solutions LLC', 101, 25000.00);
INSERT INTO `sponsor` (`Sponsor_id`, `Name`, `Event_id`, `Contribution`) VALUES (54, 'Campus Bookstore', 104, 2000.00);
INSERT INTO `sponsor` (`Sponsor_id`, `Name`, `Event_id`, `Contribution`) VALUES (55, 'sathvik the great', 105, 70000.00);

-- Dumping data for table volunteers
INSERT INTO `volunteers` (`Volunteer_id`, `Name`, `Email`, `Contact`, `Type`, `Event_id`) VALUES (201, 'Rahul Verma', 'rahul.v@vol.com', '9911223344', 'Registration Desk', 101);
INSERT INTO `volunteers` (`Volunteer_id`, `Name`, `Email`, `Contact`, `Type`, `Event_id`) VALUES (202, 'Sana Khan', 'sana.k@vol.com', '9823456789', 'Security', 103);
INSERT INTO `volunteers` (`Volunteer_id`, `Name`, `Email`, `Contact`, `Type`, `Event_id`) VALUES (203, 'Alok Gupta', 'alok.g@vol.com', '9008877665', 'Stage Management', 102);
INSERT INTO `volunteers` (`Volunteer_id`, `Name`, `Email`, `Contact`, `Type`, `Event_id`) VALUES (204, 'Meera Joshi', 'meera.j@vol.com', '7755331199', 'Logistics', 101);
INSERT INTO `volunteers` (`Volunteer_id`, `Name`, `Email`, `Contact`, `Type`, `Event_id`) VALUES (205, 'Deepak Rao', 'deepak_r@vol.com', '8844466220', 'Hospitality', 105);
INSERT INTO `volunteers` (`Volunteer_id`, `Name`, `Email`, `Contact`, `Type`, `Event_id`) VALUES (206, 'Araham', 'araham@gmail.com', '9852014562', 'Security', 105);

-- Routine: FN_GetAvailableCapacity
CREATE DEFINER=`root`@`localhost` FUNCTION `FN_GetAvailableCapacity`(p_event_id INT) RETURNS int
    READS SQL DATA
BEGIN
    DECLARE v_capacity INT;
    DECLARE v_tickets_sold INT;
    
    SELECT V.Capacity INTO v_capacity
    FROM Event E JOIN Venue V ON E.Venue_id = V.Venue_id
    WHERE E.Event_id = p_event_id;
    
    SELECT COUNT(*) INTO v_tickets_sold
    FROM Ticket
    WHERE Event_id = p_event_id AND Status = 'Confirmed';
    
    RETURN v_capacity - v_tickets_sold;
END

-- Routine: SP_ConfirmPayment
CREATE DEFINER=`root`@`localhost` PROCEDURE `SP_ConfirmPayment`(
    IN p_ticket_id INT,
    IN p_payment_method VARCHAR(50),
    IN p_amount DECIMAL(10, 2)
)
BEGIN
    INSERT INTO Payment (Ticket_id, Amount, Method, Date)
    VALUES (p_ticket_id, p_amount, p_payment_method, CURDATE());

    UPDATE Ticket
    SET Status = 'Confirmed'
    WHERE Ticket_id = p_ticket_id;

    SELECT CONCAT('Ticket ', p_ticket_id, ' confirmed and payment recorded.') AS StatusMessage;
END

-- Trigger: TR_CheckCapacityBeforeSale
CREATE DEFINER=`root`@`localhost` TRIGGER `TR_CheckCapacityBeforeSale` BEFORE INSERT ON `ticket` FOR EACH ROW BEGIN
    DECLARE v_available_capacity INT;
    SET v_available_capacity = FN_GetAvailableCapacity(NEW.Event_id);
    
    IF v_available_capacity <= 0 AND NEW.Status = 'Confirmed' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot sell ticket: Event capacity is full.';
    END IF;
END

-- Routine: FN_GetTotalConfirmedTickets
CREATE DEFINER=`root`@`localhost` FUNCTION `FN_GetTotalConfirmedTickets`(p_event_id INT) RETURNS int
    READS SQL DATA
BEGIN
    DECLARE confirmed_count INT;

    SELECT COUNT(Ticket_id)
    INTO confirmed_count
    FROM Ticket
    WHERE Event_id = p_event_id AND Status = 'Confirmed';

    RETURN confirmed_count;
END

-- Routine: SP_MarkTicketAsPending
CREATE DEFINER=`root`@`localhost` PROCEDURE `SP_MarkTicketAsPending`(
    IN p_ticket_id INT
)
BEGIN
    UPDATE Ticket
    SET Status = 'Pending'
    WHERE Ticket_id = p_ticket_id;
    SELECT CONCAT('Ticket ', p_ticket_id, ' status set to Pending.') AS StatusMessage;
END

-- Routine: SP_GetEventSummary
CREATE DEFINER=`root`@`localhost` PROCEDURE `SP_GetEventSummary`(
    IN p_event_id INT
)
BEGIN
    SELECT
        E.Name AS Event_Name,
        V.Name AS Venue_Name,
        V.Capacity
    FROM
        Event E
    JOIN
        Venue V ON E.Venue_id = V.Venue_id
    WHERE
        E.Event_id = p_event_id;
END

-- Routine: FN_GetOrganizerName (Fixed from FN_CetOrganizerName typo)
CREATE DEFINER=`root`@`localhost` FUNCTION `FN_GetOrganizerName`(p_organizer_id INT) RETURNS varchar(100) CHARSET utf8mb4
    READS SQL DATA
BEGIN
    DECLARE organizer_name VARCHAR(100);
    SELECT Name
    INTO organizer_name
    FROM Organizer
    WHERE Organizer_id = p_organizer_id;
    RETURN organizer_name;
END

-- Trigger: TR_CheckTicketPrice (Fixed FOR EACH ROW and SQLSTATE)
CREATE DEFINER=`root`@`localhost` TRIGGER `TR_CheckTicketPrice` BEFORE INSERT ON `ticket` FOR EACH ROW BEGIN
    IF NEW.Price <= 0.00 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Ticket price must be greater than zero.';
    END IF;
END

-- Trigger: TR_UpdateVolunteerOnEventDelete (Fixed FOR EACH ROW)
CREATE DEFINER=`root`@`localhost` TRIGGER `TR_UpdateVolunteerOnEventDelete` AFTER DELETE ON `event` FOR EACH ROW BEGIN
    INSERT INTO Log (Log_Message)
    VALUES (CONCAT('Event ', OLD.Event_id, ' {', OLD.Name, '} was deleted. Volunteers may need re-assignment.'));
END