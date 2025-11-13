#!/usr/bin/env python3
"""
Event Management System - Desktop Application
A comprehensive GUI application for managing events, participants, tickets, and payments.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime, date
import json
import os
from typing import Dict, List, Tuple, Optional
import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG

# Color scheme
COLORS = {
    'primary': '#2563eb',
    'secondary': '#64748b',
    'accent': '#f59e0b',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'bg': '#f8fafc',
    'card_bg': '#ffffff',
    'text': '#1e293b',
    'text_secondary': '#64748b'
}

class Database:
    """MySQL database class for Event Management System"""
    
    def __init__(self):
        """Initialize database connection"""
        self.connection = None
        self.connect()
        self.logs = []  # In-memory logs (could be moved to database)
        
        # Load initial data into memory for caching
        self.refresh_all_data()
    
    def connect(self):
        """Establish MySQL database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
        except Error as e:
            messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
            self.connection = None
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute a SQL query"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return True
        except Error as e:
            print(f"Error executing query: {e}")
            # Only show error dialog for critical errors, not for missing Log table
            if "Table" not in str(e) or "log" not in str(e).lower():
                messagebox.showerror("Database Error", f"Query error: {e}")
            return [] if fetch else False
    
    def refresh_all_data(self):
        """Refresh all data from database"""
        self.organizers = self.execute_query("SELECT * FROM Organizer", fetch=True) or []
        self.venues = self.execute_query("SELECT * FROM Venue", fetch=True) or []
        self.participants = self.execute_query("SELECT * FROM Participants", fetch=True) or []
        self.events = self.execute_query("SELECT * FROM Event", fetch=True) or []
        self.sponsors = self.execute_query("SELECT * FROM Sponsor", fetch=True) or []
        self.volunteers = self.execute_query("SELECT * FROM Volunteers", fetch=True) or []
        self.tickets = self.execute_query("SELECT * FROM Ticket", fetch=True) or []
        self.payments = self.execute_query("SELECT * FROM Payment", fetch=True) or []
        # Load users table for public login (if exists)
        try:
            self.users = self.execute_query("SELECT * FROM users", fetch=True) or []
        except:
            self.users = []
        
        # Load logs if Log table exists
        try:
            logs_data = self.execute_query("SELECT * FROM Log ORDER BY Timestamp DESC LIMIT 100", fetch=True)
            if logs_data:
                self.logs = [{'timestamp': str(log['Timestamp']), 'message': log['Log_Message']} for log in logs_data]
        except:
            pass
    
    def export_to_sql_file(self, filename: str = "dbms.sql"):
        """Export current database state to SQL file"""
        try:
            sql_content = []
            
            # Header
            sql_content.append("-- Dumped by Event Management App")
            sql_content.append("-- Auto-generated on: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            sql_content.append("DROP DATABASE IF EXISTS Event_Management_DB;")
            sql_content.append("CREATE DATABASE Event_Management_DB;")
            sql_content.append("USE Event_Management_DB;\n")
            
            # Get table structures using SHOW CREATE TABLE
            tables = ['organizer', 'venue', 'event', 'participants', 'ticket', 'payment', 'sponsor', 'volunteers', 'log']
            
            for table in tables:
                try:
                    # Get CREATE TABLE statement
                    cursor = self.connection.cursor()
                    cursor.execute(f"SHOW CREATE TABLE {table}")
                    create_stmt = cursor.fetchone()
                    if create_stmt:
                        sql_content.append(f"\n-- Table structure for {table}")
                        sql_content.append(create_stmt[1] + ";\n")
                    cursor.close()
                except:
                    pass  # Table might not exist
            
            # Export data for each table
            # Organizers
            sql_content.append("\n-- Dumping data for table organizer")
            for org in self.organizers:
                sql_content.append(
                    f"INSERT INTO `organizer` (`Organizer_id`, `Name`, `Contact`, `Email`) "
                    f"VALUES ({org['Organizer_id']}, '{org['Name']}', '{org['Contact']}', '{org['Email']}');"
                )
            
            # Venues
            sql_content.append("\n-- Dumping data for table venue")
            for venue in self.venues:
                sql_content.append(
                    f"INSERT INTO `venue` (`Venue_id`, `Name`, `Location`, `Capacity`) "
                    f"VALUES ({venue['Venue_id']}, '{venue['Name']}', '{venue['Location']}', {venue['Capacity']});"
                )
            
            # Events
            sql_content.append("\n-- Dumping data for table event")
            for event in self.events:
                sql_content.append(
                    f"INSERT INTO `event` (`Event_id`, `Name`, `Type`, `Date`, `Time`, `Venue_id`, `Organizer_id`) "
                    f"VALUES ({event['Event_id']}, '{event['Name']}', '{event['Type']}', '{event['Date']}', "
                    f"'{event['Time']}', {event['Venue_id']}, {event['Organizer_id']});"
                )
            
            # Participants
            sql_content.append("\n-- Dumping data for table participants")
            for part in self.participants:
                sql_content.append(
                    f"INSERT INTO `participants` (`Participant_id`, `Name`, `Email`, `Contact`) "
                    f"VALUES ({part['Participant_id']}, '{part['Name']}', '{part['Email']}', '{part['Contact']}');"
                )
            
            # Tickets
            sql_content.append("\n-- Dumping data for table ticket")
            for ticket in self.tickets:
                sql_content.append(
                    f"INSERT INTO `ticket` (`Ticket_id`, `Event_id`, `Participant_id`, `Status`, `Price`) "
                    f"VALUES ({ticket['Ticket_id']}, {ticket['Event_id']}, {ticket['Participant_id']}, "
                    f"'{ticket['Status']}', {ticket['Price']});"
                )
            
            # Payments
            sql_content.append("\n-- Dumping data for table payment")
            for payment in self.payments:
                sql_content.append(
                    f"INSERT INTO `payment` (`Payment_id`, `Ticket_id`, `Amount`, `Method`, `Date`) "
                    f"VALUES ({payment['Payment_id']}, {payment['Ticket_id']}, {payment['Amount']}, "
                    f"'{payment['Method']}', '{payment['Date']}');"
                )
            
            # Sponsors
            sql_content.append("\n-- Dumping data for table sponsor")
            for sponsor in self.sponsors:
                sql_content.append(
                    f"INSERT INTO `sponsor` (`Sponsor_id`, `Name`, `Event_id`, `Contribution`) "
                    f"VALUES ({sponsor['Sponsor_id']}, '{sponsor['Name']}', {sponsor['Event_id']}, "
                    f"{sponsor['Contribution']});"
                )
            
            # Volunteers
            sql_content.append("\n-- Dumping data for table volunteers")
            for vol in self.volunteers:
                sql_content.append(
                    f"INSERT INTO `volunteers` (`Volunteer_id`, `Name`, `Email`, `Contact`, `Type`, `Event_id`) "
                    f"VALUES ({vol['Volunteer_id']}, '{vol['Name']}', '{vol['Email']}', '{vol['Contact']}', "
                    f"'{vol['Type']}', {vol['Event_id']});"
                )
            
            # Add stored procedures, functions, and triggers
            sql_content.append("\n-- Routine: FN_GetAvailableCapacity")
            sql_content.append("""CREATE DEFINER=`root`@`localhost` FUNCTION `FN_GetAvailableCapacity`(p_event_id INT) RETURNS int
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
END""")
            
            sql_content.append("\n-- Routine: SP_ConfirmPayment")
            sql_content.append("""CREATE DEFINER=`root`@`localhost` PROCEDURE `SP_ConfirmPayment`(
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
END""")
            
            sql_content.append("\n-- Trigger: TR_CheckCapacityBeforeSale")
            sql_content.append("""CREATE DEFINER=`root`@`localhost` TRIGGER `TR_CheckCapacityBeforeSale` BEFORE INSERT ON `ticket` FOR EACH ROW BEGIN
    DECLARE v_available_capacity INT;
    SET v_available_capacity = FN_GetAvailableCapacity(NEW.Event_id);
    
    IF v_available_capacity <= 0 AND NEW.Status = 'Confirmed' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot sell ticket: Event capacity is full.';
    END IF;
END""")
            
            sql_content.append("\n-- Routine: FN_GetTotalConfirmedTickets")
            sql_content.append("""CREATE DEFINER=`root`@`localhost` FUNCTION `FN_GetTotalConfirmedTickets`(p_event_id INT) RETURNS int
    READS SQL DATA
BEGIN
    DECLARE confirmed_count INT;

    SELECT COUNT(Ticket_id)
    INTO confirmed_count
    FROM Ticket
    WHERE Event_id = p_event_id AND Status = 'Confirmed';

    RETURN confirmed_count;
END""")
            
            sql_content.append("\n-- Routine: SP_MarkTicketAsPending")
            sql_content.append("""CREATE DEFINER=`root`@`localhost` PROCEDURE `SP_MarkTicketAsPending`(
    IN p_ticket_id INT
)
BEGIN
    UPDATE Ticket
    SET Status = 'Pending'
    WHERE Ticket_id = p_ticket_id;
    SELECT CONCAT('Ticket ', p_ticket_id, ' status set to Pending.') AS StatusMessage;
END""")
            
            sql_content.append("\n-- Routine: SP_GetEventSummary")
            sql_content.append("""CREATE DEFINER=`root`@`localhost` PROCEDURE `SP_GetEventSummary`(
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
END""")
            
            sql_content.append("\n-- Routine: FN_GetOrganizerName (Fixed from FN_CetOrganizerName typo)")
            sql_content.append("""CREATE DEFINER=`root`@`localhost` FUNCTION `FN_GetOrganizerName`(p_organizer_id INT) RETURNS varchar(100) CHARSET utf8mb4
    READS SQL DATA
BEGIN
    DECLARE organizer_name VARCHAR(100);
    SELECT Name
    INTO organizer_name
    FROM Organizer
    WHERE Organizer_id = p_organizer_id;
    RETURN organizer_name;
END""")
            
            sql_content.append("\n-- Trigger: TR_CheckTicketPrice (Fixed FOR EACH ROW and SQLSTATE)")
            sql_content.append("""CREATE DEFINER=`root`@`localhost` TRIGGER `TR_CheckTicketPrice` BEFORE INSERT ON `ticket` FOR EACH ROW BEGIN
    IF NEW.Price <= 0.00 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Ticket price must be greater than zero.';
    END IF;
END""")
            
            sql_content.append("\n-- Trigger: TR_UpdateVolunteerOnEventDelete (Fixed FOR EACH ROW)")
            sql_content.append("""CREATE DEFINER=`root`@`localhost` TRIGGER `TR_UpdateVolunteerOnEventDelete` AFTER DELETE ON `event` FOR EACH ROW BEGIN
    INSERT INTO Log (Log_Message)
    VALUES (CONCAT('Event ', OLD.Event_id, ' {', OLD.Name, '} was deleted. Volunteers may need re-assignment.'));
END""")
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sql_content))
            
            print(f"Database exported to {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting to SQL file: {e}")
            return False
    
    # CRUD Operations for Events
    def add_event(self, event_data: Dict) -> bool:
        """Add new event to database"""
        query = """INSERT INTO Event (Event_id, Name, Type, Date, Time, Venue_id, Organizer_id) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        params = (event_data['Event_id'], event_data['Name'], event_data['Type'],
                 event_data['Date'], event_data['Time'], event_data['Venue_id'], event_data['Organizer_id'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def update_event(self, event_data: Dict) -> bool:
        """Update existing event"""
        query = """UPDATE Event SET Name=%s, Type=%s, Date=%s, Time=%s, Venue_id=%s, Organizer_id=%s 
                   WHERE Event_id=%s"""
        params = (event_data['Name'], event_data['Type'], event_data['Date'], 
                 event_data['Time'], event_data['Venue_id'], event_data['Organizer_id'], event_data['Event_id'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def delete_event(self, event_id: int, event_name: str) -> bool:
        """Delete event from database with full cascade"""
        # Log the deletion first
        self.log_event_deletion(event_id, event_name)
        
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            
            # Delete related records in correct order to respect foreign keys
            # 1. Get all tickets for this event
            cursor.execute("SELECT Ticket_id FROM Ticket WHERE Event_id=%s", (event_id,))
            tickets = cursor.fetchall()
            
            # 2. Delete payments for each ticket
            for ticket in tickets:
                cursor.execute("DELETE FROM Payment WHERE Ticket_id=%s", (ticket['Ticket_id'],))
            
            # 3. Delete all tickets for this event
            cursor.execute("DELETE FROM Ticket WHERE Event_id=%s", (event_id,))
            
            # 4. Delete all volunteers assigned to this event
            cursor.execute("DELETE FROM Volunteers WHERE Event_id=%s", (event_id,))
            
            # 5. Delete all sponsors for this event
            cursor.execute("DELETE FROM Sponsor WHERE Event_id=%s", (event_id,))
            
            # 6. Finally delete the event itself
            cursor.execute("DELETE FROM Event WHERE Event_id=%s", (event_id,))
            
            self.connection.commit()
            cursor.close()
            
            # Refresh all data from database
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
            return True
            
        except Error as e:
            print(f"Error deleting event with cascade: {e}")
            messagebox.showerror("Database Error", f"Failed to delete event: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    # CRUD Operations for Tickets
    def add_ticket(self, ticket_data: Dict) -> bool:
        """Add new ticket to database"""
        query = """INSERT INTO Ticket (Ticket_id, Event_id, Participant_id, Status, Price) 
                   VALUES (%s, %s, %s, %s, %s)"""
        params = (ticket_data['Ticket_id'], ticket_data['Event_id'], ticket_data['Participant_id'],
                 ticket_data['Status'], ticket_data['Price'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def update_ticket(self, ticket_data: Dict) -> bool:
        """Update existing ticket"""
        query = """UPDATE Ticket SET Event_id=%s, Participant_id=%s, Status=%s, Price=%s 
                   WHERE Ticket_id=%s"""
        params = (ticket_data['Event_id'], ticket_data['Participant_id'], ticket_data['Status'],
                 ticket_data['Price'], ticket_data['Ticket_id'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def delete_ticket(self, ticket_id: int) -> bool:
        """Delete ticket from database"""
        # Delete payment first if exists
        self.execute_query("DELETE FROM Payment WHERE Ticket_id=%s", (ticket_id,))
        
        query = "DELETE FROM Ticket WHERE Ticket_id=%s"
        result = self.execute_query(query, (ticket_id,))
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    # CRUD Operations for Participants
    def add_participant(self, participant_data: Dict) -> bool:
        """Add new participant to database"""
        query = """INSERT INTO Participants (Participant_id, Name, Email, Contact) 
                   VALUES (%s, %s, %s, %s)"""
        params = (participant_data['Participant_id'], participant_data['Name'],
                 participant_data['Email'], participant_data['Contact'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def update_participant(self, participant_data: Dict) -> bool:
        """Update existing participant"""
        query = """UPDATE Participants SET Name=%s, Email=%s, Contact=%s 
                   WHERE Participant_id=%s"""
        params = (participant_data['Name'], participant_data['Email'],
                 participant_data['Contact'], participant_data['Participant_id'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def delete_participant(self, participant_id: int) -> bool:
        """Delete participant from database"""
        query = "DELETE FROM Participants WHERE Participant_id=%s"
        result = self.execute_query(query, (participant_id,))
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    # CRUD Operations for Volunteers
    def add_volunteer(self, volunteer_data: Dict) -> bool:
        """Add new volunteer to database"""
        query = """INSERT INTO Volunteers (Volunteer_id, Name, Email, Contact, Type, Event_id) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        params = (volunteer_data['Volunteer_id'], volunteer_data['Name'], volunteer_data['Email'],
                 volunteer_data['Contact'], volunteer_data['Type'], volunteer_data['Event_id'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def update_volunteer(self, volunteer_data: Dict) -> bool:
        """Update existing volunteer"""
        query = """UPDATE Volunteers SET Name=%s, Email=%s, Contact=%s, Type=%s, Event_id=%s 
                   WHERE Volunteer_id=%s"""
        params = (volunteer_data['Name'], volunteer_data['Email'], volunteer_data['Contact'],
                 volunteer_data['Type'], volunteer_data['Event_id'], volunteer_data['Volunteer_id'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def delete_volunteer(self, volunteer_id: int) -> bool:
        """Delete volunteer from database"""
        query = "DELETE FROM Volunteers WHERE Volunteer_id=%s"
        result = self.execute_query(query, (volunteer_id,))
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    # CRUD Operations for Venues
    def add_venue(self, venue_data: Dict) -> bool:
        """Add new venue to database"""
        query = """INSERT INTO Venue (Venue_id, Name, Location, Capacity) 
                   VALUES (%s, %s, %s, %s)"""
        params = (venue_data['Venue_id'], venue_data['Name'],
                 venue_data['Location'], venue_data['Capacity'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def update_venue(self, venue_data: Dict) -> bool:
        """Update existing venue"""
        query = """UPDATE Venue SET Name=%s, Location=%s, Capacity=%s 
                   WHERE Venue_id=%s"""
        params = (venue_data['Name'], venue_data['Location'],
                 venue_data['Capacity'], venue_data['Venue_id'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def delete_venue(self, venue_id: int) -> bool:
        """Delete venue from database"""
        query = "DELETE FROM Venue WHERE Venue_id=%s"
        result = self.execute_query(query, (venue_id,))
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    # CRUD Operations for Sponsors
    def add_sponsor(self, sponsor_data: Dict) -> bool:
        """Add new sponsor to database"""
        query = """INSERT INTO Sponsor (Sponsor_id, Name, Event_id, Contribution) 
                   VALUES (%s, %s, %s, %s)"""
        params = (sponsor_data['Sponsor_id'], sponsor_data['Name'],
                 sponsor_data['Event_id'], sponsor_data['Contribution'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def update_sponsor(self, sponsor_data: Dict) -> bool:
        """Update existing sponsor"""
        query = """UPDATE Sponsor SET Name=%s, Event_id=%s, Contribution=%s 
                   WHERE Sponsor_id=%s"""
        params = (sponsor_data['Name'], sponsor_data['Event_id'],
                 sponsor_data['Contribution'], sponsor_data['Sponsor_id'])
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    def delete_sponsor(self, sponsor_id: int) -> bool:
        """Delete sponsor from database"""
        query = "DELETE FROM Sponsor WHERE Sponsor_id=%s"
        result = self.execute_query(query, (sponsor_id,))
        if result:
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
        return result
    
    # Functions and Procedures
    def get_available_capacity(self, event_id: int) -> int:
        """Get available capacity for an event"""
        try:
            # Try using the MySQL function first
            result = self.execute_query("SELECT FN_GetAvailableCapacity(%s) as capacity", 
                                      (event_id,), fetch=True)
            if result and result[0]['capacity'] is not None:
                return result[0]['capacity']
        except:
            pass
        
        # Fallback to direct SQL query
        try:
            result = self.execute_query("""
                SELECT v.Capacity - COUNT(t.Ticket_id) as capacity
                FROM Event e
                JOIN Venue v ON e.Venue_id = v.Venue_id
                LEFT JOIN Ticket t ON e.Event_id = t.Event_id AND t.Status = 'Confirmed'
                WHERE e.Event_id = %s
                GROUP BY v.Capacity
            """, (event_id,), fetch=True)
            if result:
                return result[0]['capacity']
        except:
            pass
        
        # Last resort: use cached data
        event = next((e for e in self.events if e['Event_id'] == event_id), None)
        if not event:
            return 0
        venue = next((v for v in self.venues if v['Venue_id'] == event['Venue_id']), None)
        if not venue:
            return 0
        confirmed_tickets = sum(1 for t in self.tickets 
                               if t['Event_id'] == event_id and t['Status'] == 'Confirmed')
        return venue['Capacity'] - confirmed_tickets
    
    def confirm_payment(self, ticket_id: int, payment_method: str, amount: float) -> str:
        """Procedure SP_ConfirmPayment - Call MySQL stored procedure"""
        try:
            cursor = self.connection.cursor()
            cursor.callproc('SP_ConfirmPayment', (ticket_id, payment_method, amount))
            
            # Get the result
            for result in cursor.stored_results():
                row = result.fetchone()
                message = row[0] if row else "Payment processed"
            
            self.connection.commit()
            cursor.close()
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
            return message
        except Error as e:
            # Fallback to manual implementation
            ticket = next((t for t in self.tickets if t['Ticket_id'] == ticket_id), None)
            if not ticket:
                return f"Error: Ticket {ticket_id} not found"
            
            if ticket['Status'] == 'Cancelled':
                return f"Error: Cannot process payment for cancelled ticket {ticket_id}"
            
            # Check for existing payment
            existing_payment = next((p for p in self.payments if p['Ticket_id'] == ticket_id), None)
            if existing_payment:
                if ticket['Status'] == 'Pending':
                    # Update status
                    self.execute_query("UPDATE Ticket SET Status='Confirmed' WHERE Ticket_id=%s", (ticket_id,))
                    self.refresh_all_data()
                    self.export_to_sql_file()  # Auto-export to SQL file
                    return f"Ticket {ticket_id} confirmed. Payment already on record."
                return f"Error: Payment already exists for ticket {ticket_id}"
            
            # Create payment
            query = """INSERT INTO Payment (Ticket_id, Amount, Method, Date) 
                      VALUES (%s, %s, %s, CURDATE())"""
            self.execute_query(query, (ticket_id, amount, payment_method))
            
            # Update ticket status
            self.execute_query("UPDATE Ticket SET Status='Confirmed' WHERE Ticket_id=%s", (ticket_id,))
            self.refresh_all_data()
            self.export_to_sql_file()  # Auto-export to SQL file
            return f"Ticket {ticket_id} confirmed and payment recorded."
    
    def get_total_confirmed_tickets(self, event_id: int) -> int:
        """Get total confirmed tickets for an event"""
        try:
            # Try using the MySQL function first
            result = self.execute_query("SELECT FN_GetTotalConfirmedTickets(%s) as count", 
                                      (event_id,), fetch=True)
            if result and result[0]['count'] is not None:
                return result[0]['count']
        except:
            pass
        
        # Fallback to direct SQL query
        try:
            result = self.execute_query(
                "SELECT COUNT(*) as count FROM Ticket WHERE Event_id=%s AND Status='Confirmed'",
                (event_id,), fetch=True
            )
            return result[0]['count'] if result else 0
        except:
            # Last resort: use cached data
            return sum(1 for t in self.tickets 
                      if t['Event_id'] == event_id and t['Status'] == 'Confirmed')
    
    def mark_ticket_as_pending(self, ticket_id: int) -> str:
        """Procedure SP_MarkTicketAsPending - Call MySQL stored procedure"""
        try:
            cursor = self.connection.cursor()
            cursor.callproc('SP_MarkTicketAsPending', (ticket_id,))
            
            for result in cursor.stored_results():
                row = result.fetchone()
                message = row[0] if row else f"Ticket {ticket_id} status set to Pending."
            
            self.connection.commit()
            cursor.close()
            self.refresh_all_data()
            return message
        except Error as e:
            # Fallback
            query = "UPDATE Ticket SET Status='Pending' WHERE Ticket_id=%s"
            if self.execute_query(query, (ticket_id,)):
                self.refresh_all_data()
                return f"Ticket {ticket_id} status set to Pending."
            return f"Error: Could not update ticket {ticket_id}"
    
    def get_event_summary(self, event_id: int) -> Dict:
        """Procedure SP_GetEventSummary - Call MySQL stored procedure"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.callproc('SP_GetEventSummary', (event_id,))
            
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    cursor.close()
                    return {
                        'Event_Name': row['Event_Name'],
                        'Venue_Name': row['Venue_Name'],
                        'Capacity': row['Capacity'],
                        'Available': self.get_available_capacity(event_id),
                        'Confirmed_Tickets': self.get_total_confirmed_tickets(event_id)
                    }
            cursor.close()
        except:
            pass
        
        # Fallback
        event = next((e for e in self.events if e['Event_id'] == event_id), None)
        if not event:
            return {'error': f"Event {event_id} not found"}
        venue = next((v for v in self.venues if v['Venue_id'] == event['Venue_id']), None)
        if not venue:
            return {'error': 'Venue not found'}
        
        return {
            'Event_Name': event['Name'],
            'Venue_Name': venue['Name'],
            'Capacity': venue['Capacity'],
            'Available': self.get_available_capacity(event_id),
            'Confirmed_Tickets': self.get_total_confirmed_tickets(event_id)
        }
    
    def get_organizer_name(self, organizer_id: int) -> str:
        """Get organizer name by ID"""
        try:
            # Try using the MySQL function first
            result = self.execute_query("SELECT FN_GetOrganizerName(%s) as name", 
                                      (organizer_id,), fetch=True)
            if result and result[0]['name']:
                return result[0]['name']
        except:
            pass
        
        # Fallback to direct SQL query
        try:
            result = self.execute_query("SELECT Name FROM Organizer WHERE Organizer_id=%s",
                                      (organizer_id,), fetch=True)
            if result and result[0]['Name']:
                return result[0]['Name']
        except:
            pass
        
        # Last resort: use cached data
        organizer = next((o for o in self.organizers if o['Organizer_id'] == organizer_id), None)
        return organizer['Name'] if organizer else 'Unknown'
    
    def check_ticket_price(self, price: float) -> bool:
        """Trigger TR_CheckTicketPrice validation"""
        if price <= 0.00:
            raise ValueError("Ticket price must be greater than zero.")
        return True
    
    def log_event_deletion(self, event_id: int, event_name: str):
        """Trigger TR_UpdateVolunteerOnEventDelete - Log to database"""
        log_message = f"Event {event_id} ({event_name}) was deleted. Volunteers may need re-assignment."
        
        # Try to insert into Log table
        try:
            query = "INSERT INTO Log (Log_Message) VALUES (%s)"
            self.execute_query(query, (log_message,))
        except:
            pass
        
        # Also keep in memory
        self.logs.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': log_message
        })
    
    def __del__(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    # --- User & public registration helpers ---
    def get_next_participant_id(self) -> int:
        """Return next Participant_id (simple increment based on cache)"""
        try:
            max_id = max((p['Participant_id'] for p in self.participants), default=1000)
            return int(max_id) + 1
        except Exception:
            return 1001

    def get_next_volunteer_id(self) -> int:
        """Return next Volunteer_id (simple increment based on cache)"""
        try:
            max_id = max((v['Volunteer_id'] for v in self.volunteers), default=200)
            return int(max_id) + 1
        except Exception:
            return 201

    def add_user(self, user_data: Dict) -> bool:
        """Add a new user to users table"""
        query = "INSERT INTO users (User_id, Username, Password, Fullname, Email, Role) VALUES (%s,%s,%s,%s,%s,%s)"
        params = (user_data.get('User_id'), user_data.get('Username'), user_data.get('Password'),
                  user_data.get('Fullname'), user_data.get('Email'), user_data.get('Role', 'user'))
        result = self.execute_query(query, params)
        if result:
            self.refresh_all_data()
        return result

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate against `users` table or cached users; returns user dict on success"""
        # Check cached users first
        for u in getattr(self, 'users', []):
            if u.get('Username') == username and u.get('Password') == password:
                return u

        # Fallback to DB lookup
        try:
            res = self.execute_query("SELECT * FROM users WHERE Username=%s AND Password=%s", (username, password), fetch=True)
            if res:
                return res[0]
        except:
            pass
        return None

    def register_user_as_participant(self, username: str, event_id: int, fullname: str, email: str, contact: str) -> Tuple[bool, str]:
        """Register a logged-in user as a participant for an event (creates Participant). Returns (ok, message)."""
        try:
            new_pid = self.get_next_participant_id()
            query = "INSERT INTO Participants (Participant_id, Name, Email, Contact) VALUES (%s, %s, %s, %s)"
            if not self.execute_query(query, (new_pid, fullname, email, contact)):
                return False, "Failed to create participant record"

            # Optionally create a pending ticket with a minimal price (0.01) to avoid triggers blocking
            new_tid = max((t['Ticket_id'] for t in self.tickets), default=3000) + 1
            ticket_query = "INSERT INTO Ticket (Ticket_id, Event_id, Participant_id, Status, Price) VALUES (%s,%s,%s,%s,%s)"
            if not self.execute_query(ticket_query, (new_tid, event_id, new_pid, 'Pending', 0.01)):
                return False, "Participant created but failed to create ticket"

            self.refresh_all_data()
            self.export_to_sql_file()
            return True, f"Registered as participant (Participant ID: {new_pid}, Ticket ID: {new_tid})"
        except Exception as e:
            return False, str(e)

    def register_user_as_volunteer(self, username: str, event_id: int, fullname: str, email: str, contact: str, vtype: str = 'General') -> Tuple[bool, str]:
        """Register a logged-in user as a volunteer for an event (creates Volunteers)."""
        try:
            new_vid = self.get_next_volunteer_id()
            query = "INSERT INTO Volunteers (Volunteer_id, Name, Email, Contact, Type, Event_id) VALUES (%s,%s,%s,%s,%s,%s)"
            if not self.execute_query(query, (new_vid, fullname, email, contact, vtype, event_id)):
                return False, "Failed to create volunteer record"

            self.refresh_all_data()
            self.export_to_sql_file()
            return True, f"Registered as volunteer (Volunteer ID: {new_vid})"
        except Exception as e:
            return False, str(e)


class CRUDDialog(tk.Toplevel):
    """Generic CRUD dialog for data entry/editing"""
    
    def __init__(self, parent, title: str, fields: List[Dict], data: Optional[Dict] = None):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x600")
        self.resizable(False, False)
        
        self.result = None
        self.fields = fields
        self.entries = {}
        
        # Create form
        self.create_form(data)
        
        # Create buttons
        self.create_buttons()
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
    def create_form(self, data: Optional[Dict]):
        """Create form fields"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        for i, field in enumerate(self.fields):
            # Label
            label = ttk.Label(main_frame, text=field['label'] + ":")
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            
            # Entry widget based on type
            if field['type'] == 'dropdown':
                widget = ttk.Combobox(main_frame, width=30)
                widget['values'] = field['values']
                if data and field['name'] in data:
                    widget.set(data[field['name']])
            elif field['type'] == 'text':
                widget = ttk.Entry(main_frame, width=32)
                if data and field['name'] in data:
                    widget.insert(0, data[field['name']])
            elif field['type'] == 'number':
                widget = ttk.Entry(main_frame, width=32)
                if data and field['name'] in data:
                    widget.insert(0, str(data[field['name']]))
            elif field['type'] == 'date':
                widget = ttk.Entry(main_frame, width=32)
                if data and field['name'] in data:
                    widget.insert(0, data[field['name']])
                else:
                    widget.insert(0, datetime.now().strftime('%Y-%m-%d'))
            elif field['type'] == 'time':
                widget = ttk.Entry(main_frame, width=32)
                if data and field['name'] in data:
                    widget.insert(0, data[field['name']])
                else:
                    widget.insert(0, '00:00:00')
            else:
                widget = ttk.Entry(main_frame, width=32)
                if data and field['name'] in data:
                    widget.insert(0, str(data[field['name']]))
            
            widget.grid(row=i, column=1, pady=5)
            self.entries[field['name']] = widget
    
    def create_buttons(self):
        """Create dialog buttons"""
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=10)
        
        save_btn = ttk.Button(button_frame, text="Save", command=self.save)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def save(self):
        """Save form data"""
        self.result = {}
        for field in self.fields:
            widget = self.entries[field['name']]
            value = widget.get()
            
            # Type conversion
            if field['type'] == 'number':
                try:
                    value = int(value) if '.' not in value else float(value)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid number for {field['label']}")
                    return
            
            self.result[field['name']] = value
        
        self.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.result = None
        self.destroy()

class EventManagementApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Event Management System")
        self.root.geometry("1200x800")
        
        # Initialize database
        self.db = Database()
        # Currently logged-in public user (for Public Portal)
        self.current_user = None
        
        # Configure styles
        self.setup_styles()
        
        # Create main layout
        self.create_main_layout()
        
        # Create tabs
        self.create_tabs()
        
        # Load initial data
        self.refresh_all_data()
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TLabel', background=COLORS['bg'])
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('KPI.TFrame', background=COLORS['card_bg'], relief='solid', borderwidth=1)
    
    def create_main_layout(self):
        """Create the main application layout"""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = ttk.Label(header_frame, text="Event Management System", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def create_tabs(self):
        """Create all application tabs"""
        # Dashboard Tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.create_dashboard_tab()
        
        # Events Management Tab
        self.events_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.events_frame, text="Events Management")
        self.create_events_tab()
        
        # Tickets & Payments Tab
        self.tickets_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tickets_frame, text="Tickets & Payments")
        self.create_tickets_tab()
        
        # Participants & Volunteers Tab
        self.participants_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.participants_frame, text="Participants & Volunteers")
        self.create_participants_tab()
        
        # Venues & Sponsors Tab
        self.venues_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.venues_frame, text="Venues & Sponsors")
        self.create_venues_tab()
        
        # Analytics Tab
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytics & Reports")
        self.create_analytics_tab()
        
        # Advanced Features Tab
        self.advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_frame, text="Advanced Features")
        self.create_advanced_tab()

        # Public Portal Tab (for users to view events and register)
        self.public_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.public_frame, text="Public Portal")
        self.create_public_tab()
    
    def create_dashboard_tab(self):
        """Create the dashboard tab with KPIs"""
        # Header with Refresh button
        header_frame = ttk.Frame(self.dashboard_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(header_frame, text="Dashboard", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Refresh", command=self.refresh_dashboard).pack(side=tk.RIGHT, padx=5)
        
        # KPI Frame
        kpi_frame = ttk.Frame(self.dashboard_frame)
        kpi_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Create KPI cards (removed Active Events)
        kpis = [
            ("Total Events", len(self.db.events)),
            ("Total Participants", len(self.db.participants)),
            ("Total Revenue", f"${sum(p['Amount'] for p in self.db.payments):,.2f}")
        ]
        
        for i, (title, value) in enumerate(kpis):
            card = ttk.Frame(kpi_frame, style='KPI.TFrame', padding=20)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            
            title_label = ttk.Label(card, text=title, font=('Arial', 10))
            title_label.pack()
            
            value_label = ttk.Label(card, text=str(value), font=('Arial', 18, 'bold'))
            value_label.pack()
        
        # Configure grid weights
        for i in range(3):
            kpi_frame.columnconfigure(i, weight=1)
        
        # Recent Activity
        activity_label = ttk.Label(self.dashboard_frame, text="Recent Tickets", 
                                 font=('Arial', 14, 'bold'))
        activity_label.pack(padx=20, pady=(20, 5), anchor=tk.W)
        
        # Create treeview for recent tickets
        columns = ('Ticket ID', 'Event ID', 'Participant ID', 'Status', 'Price')
        self.recent_tree = ttk.Treeview(self.dashboard_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=150)
        
        self.recent_tree.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        # Load recent tickets
        recent_tickets = sorted(self.db.tickets, key=lambda x: x['Ticket_id'], reverse=True)[:10]
        for ticket in recent_tickets:
            self.recent_tree.insert('', tk.END, values=(
                ticket['Ticket_id'],
                ticket['Event_id'],
                ticket['Participant_id'],
                ticket['Status'],
                f"${ticket['Price']:.2f}"
            ))
    
    def create_events_tab(self):
        """Create the events management tab"""
        # Control frame
        control_frame = ttk.Frame(self.events_frame)
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Search
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.event_search_var = tk.StringVar()
        self.event_search_var.trace('w', self.filter_events)
        search_entry = ttk.Entry(control_frame, textvariable=self.event_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        add_btn = ttk.Button(control_frame, text="Add Event", command=self.add_event)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = ttk.Button(control_frame, text="Edit Event", command=self.edit_event)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(control_frame, text="Delete Event", command=self.delete_event)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(control_frame, text="Refresh", command=self.refresh_events)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ('Event ID', 'Name', 'Type', 'Date', 'Time', 'Venue ID', 'Organizer ID')
        self.events_tree = ttk.Treeview(self.events_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.events_tree.heading(col, text=col)
            self.events_tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.events_frame, orient=tk.VERTICAL, command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)
        
        self.events_tree.pack(side=tk.LEFT, padx=20, pady=5, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_tickets_tab(self):
        """Create the tickets and payments tab"""
        # Create paned window for split view
        paned = ttk.PanedWindow(self.tickets_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Tickets
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Tickets", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Ticket controls
        ticket_control = ttk.Frame(left_frame)
        ticket_control.pack(fill=tk.X, pady=5)
        
        add_ticket_btn = ttk.Button(ticket_control, text="Add Ticket", command=self.add_ticket)
        add_ticket_btn.pack(side=tk.LEFT, padx=5)
        
        # Tickets treeview
        ticket_columns = ('Ticket ID', 'Event ID', 'Participant ID', 'Status', 'Price')
        self.tickets_tree = ttk.Treeview(left_frame, columns=ticket_columns, show='headings', height=15)
        
        for col in ticket_columns:
            self.tickets_tree.heading(col, text=col)
            self.tickets_tree.column(col, width=100)
        
        self.tickets_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Right panel - Payments
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="Payments", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Payment processing
        payment_frame = ttk.LabelFrame(right_frame, text="Process Payment", padding=10)
        payment_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(payment_frame, text="Ticket ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.payment_ticket_var = tk.StringVar()
        ticket_combo = ttk.Combobox(payment_frame, textvariable=self.payment_ticket_var, width=20)
        ticket_combo.grid(row=0, column=1, pady=2)
        
        ttk.Label(payment_frame, text="Method:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.payment_method_var = tk.StringVar()
        method_combo = ttk.Combobox(payment_frame, textvariable=self.payment_method_var, width=20)
        method_combo['values'] = ('Credit Card', 'Debit Card', 'UPI', 'Wallet', 'Cash')
        method_combo.grid(row=1, column=1, pady=2)
        
        ttk.Label(payment_frame, text="Amount:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.payment_amount_var = tk.StringVar()
        amount_entry = ttk.Entry(payment_frame, textvariable=self.payment_amount_var, width=22)
        amount_entry.grid(row=2, column=1, pady=2)
        
        process_btn = ttk.Button(payment_frame, text="Process Payment", command=self.process_payment)
        process_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Payments treeview
        payment_columns = ('Payment ID', 'Ticket ID', 'Amount', 'Method', 'Date')
        self.payments_tree = ttk.Treeview(right_frame, columns=payment_columns, show='headings', height=10)
        
        for col in payment_columns:
            self.payments_tree.heading(col, text=col)
            self.payments_tree.column(col, width=100)
        
        self.payments_tree.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def create_participants_tab(self):
        """Create the participants and volunteers tab"""
        # Create paned window for split view
        paned = ttk.PanedWindow(self.participants_frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Top panel - Participants
        top_frame = ttk.Frame(paned)
        paned.add(top_frame, weight=1)
        
        ttk.Label(top_frame, text="Participants", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Participant controls
        part_control = ttk.Frame(top_frame)
        part_control.pack(fill=tk.X, pady=5)
        
        add_part_btn = ttk.Button(part_control, text="Add Participant", command=self.add_participant)
        add_part_btn.pack(side=tk.LEFT, padx=5)
        
        # Participants treeview
        part_columns = ('Participant ID', 'Name', 'Email', 'Contact')
        self.participants_tree = ttk.Treeview(top_frame, columns=part_columns, show='headings', height=8)
        
        for col in part_columns:
            self.participants_tree.heading(col, text=col)
            self.participants_tree.column(col, width=200)
        
        self.participants_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Bottom panel - Volunteers
        bottom_frame = ttk.Frame(paned)
        paned.add(bottom_frame, weight=1)
        
        ttk.Label(bottom_frame, text="Volunteers", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Volunteer controls
        vol_control = ttk.Frame(bottom_frame)
        vol_control.pack(fill=tk.X, pady=5)
        
        add_vol_btn = ttk.Button(vol_control, text="Add Volunteer", command=self.add_volunteer)
        add_vol_btn.pack(side=tk.LEFT, padx=5)
        
        # Volunteers treeview
        vol_columns = ('Volunteer ID', 'Name', 'Email', 'Contact', 'Type', 'Event ID')
        self.volunteers_tree = ttk.Treeview(bottom_frame, columns=vol_columns, show='headings', height=8)
        
        for col in vol_columns:
            self.volunteers_tree.heading(col, text=col)
            self.volunteers_tree.column(col, width=150)
        
        self.volunteers_tree.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def create_venues_tab(self):
        """Create the venues and sponsors tab"""
        # Create paned window for split view
        paned = ttk.PanedWindow(self.venues_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Venues
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Venues", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Venue controls
        venue_control = ttk.Frame(left_frame)
        venue_control.pack(fill=tk.X, pady=5)
        
        add_venue_btn = ttk.Button(venue_control, text="Add Venue", command=self.add_venue)
        add_venue_btn.pack(side=tk.LEFT, padx=5)
        
        # Venues treeview
        venue_columns = ('Venue ID', 'Name', 'Location', 'Capacity')
        self.venues_tree = ttk.Treeview(left_frame, columns=venue_columns, show='headings', height=15)
        
        for col in venue_columns:
            self.venues_tree.heading(col, text=col)
            self.venues_tree.column(col, width=150)
        
        self.venues_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Right panel - Sponsors
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="Sponsors", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Sponsor controls
        sponsor_control = ttk.Frame(right_frame)
        sponsor_control.pack(fill=tk.X, pady=5)
        
        add_sponsor_btn = ttk.Button(sponsor_control, text="Add Sponsor", command=self.add_sponsor)
        add_sponsor_btn.pack(side=tk.LEFT, padx=5)
        
        # Total sponsorship label
        self.total_sponsorship_label = ttk.Label(right_frame, text="", font=('Arial', 10, 'bold'))
        self.total_sponsorship_label.pack(pady=5)
        
        # Sponsors treeview
        sponsor_columns = ('Sponsor ID', 'Name', 'Event ID', 'Contribution')
        self.sponsors_tree = ttk.Treeview(right_frame, columns=sponsor_columns, show='headings', height=15)
        
        for col in sponsor_columns:
            self.sponsors_tree.heading(col, text=col)
            self.sponsors_tree.column(col, width=150)
        
        self.sponsors_tree.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def create_analytics_tab(self):
        """Create the analytics and reports tab"""
        # Create scrollable frame
        canvas = tk.Canvas(self.analytics_frame, bg=COLORS['bg'])
        scrollbar = ttk.Scrollbar(self.analytics_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title and Refresh Button Frame
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(header_frame, text="Analytics & Reports", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(header_frame, text="🔄 Refresh Data", 
                               command=self.refresh_analytics)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Report 1: Event Capacity Report
        report1_frame = ttk.LabelFrame(scrollable_frame, text="Event Capacity Report", padding=10)
        report1_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.report1_text = tk.Text(report1_frame, height=6, width=80)
        self.report1_text.pack()
        
        # Report 2: Confirmed Participants
        report2_frame = ttk.LabelFrame(scrollable_frame, text="Confirmed Participants", padding=10)
        report2_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.report2_text = tk.Text(report2_frame, height=8, width=80)
        self.report2_text.pack()
        
        # Report 3: Total Revenue by Organizer
        report3_frame = ttk.LabelFrame(scrollable_frame, text="Total Revenue by Organizer", padding=10)
        report3_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.report3_text = tk.Text(report3_frame, height=8, width=80)
        self.report3_text.pack()
        
        # Export button
        export_btn = ttk.Button(scrollable_frame, text="Export All Reports", 
                               command=self.export_reports)
        export_btn.pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initial load of data
        self.refresh_analytics()

    def create_public_tab(self):
        """Create a simple public portal for users to login and register for events"""
        main_frame = ttk.Frame(self.public_frame, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Public Portal - Login to Register", font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)

        # Login frame
        login_frame = ttk.Frame(main_frame)
        login_frame.pack(pady=5)

        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W)
        self.public_username_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.public_username_var, width=30).grid(row=0, column=1, padx=5)

        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W)
        self.public_password_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.public_password_var, width=30, show='*').grid(row=1, column=1, padx=5)

        login_btn = ttk.Button(login_frame, text="Login", command=self.public_login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=8)

        self.public_status_label = ttk.Label(main_frame, text="Not logged in", foreground='red')
        self.public_status_label.pack(pady=5)

        # Events list and action buttons
        events_frame = ttk.LabelFrame(main_frame, text="Available Events", padding=10)
        events_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ('Event ID', 'Name', 'Type', 'Date', 'Time', 'Venue')
        self.public_events_tree = ttk.Treeview(events_frame, columns=columns, show='headings', height=8)
        for col in columns:
            self.public_events_tree.heading(col, text=col)
            self.public_events_tree.column(col, width=140)
        self.public_events_tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=8)

        self.register_part_btn = ttk.Button(btn_frame, text="Register as Participant", command=self.public_register_participant)
        self.register_part_btn.pack(side=tk.LEFT, padx=5)

        self.register_vol_btn = ttk.Button(btn_frame, text="Register as Volunteer", command=self.public_register_volunteer)
        self.register_vol_btn.pack(side=tk.LEFT, padx=5)

        # Disable buttons until login
        self.register_part_btn.state(['disabled'])
        self.register_vol_btn.state(['disabled'])

        # Load events
        self.refresh_public_portal()

    def public_login(self):
        """Authenticate public user"""
        username = self.public_username_var.get().strip()
        password = self.public_password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("Login", "Please enter username and password")
            return

        user = self.db.authenticate_user(username, password)
        if user:
            self.current_user = user
            self.public_status_label.config(text=f"Logged in as: {user.get('Fullname') or user.get('Username')}", foreground='green')
            self.register_part_btn.state(['!disabled'])
            self.register_vol_btn.state(['!disabled'])
            messagebox.showinfo("Login", f"Welcome {user.get('Fullname') or user.get('Username')}!")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def public_register_participant(self):
        """Register the logged-in user as a participant for selected event"""
        if not getattr(self, 'current_user', None):
            messagebox.showwarning("Not logged in", "Please login first")
            return

        sel = self.public_events_tree.selection()
        if not sel:
            messagebox.showwarning("Select Event", "Please select an event to register for")
            return
        item = self.public_events_tree.item(sel[0])
        event_id = int(item['values'][0])

        fullname = self.current_user.get('Fullname') or self.current_user.get('Username')
        email = self.current_user.get('Email') or ''
        contact = ''

        ok, msg = self.db.register_user_as_participant(self.current_user.get('Username'), event_id, fullname, email, contact)
        if ok:
            messagebox.showinfo("Registered", msg)
            self.refresh_all_data()
            self.refresh_public_portal()
        else:
            messagebox.showerror("Error", msg)

    def public_register_volunteer(self):
        """Register the logged-in user as a volunteer for selected event"""
        if not getattr(self, 'current_user', None):
            messagebox.showwarning("Not logged in", "Please login first")
            return

        sel = self.public_events_tree.selection()
        if not sel:
            messagebox.showwarning("Select Event", "Please select an event to volunteer for")
            return
        item = self.public_events_tree.item(sel[0])
        event_id = int(item['values'][0])

        fullname = self.current_user.get('Fullname') or self.current_user.get('Username')
        email = self.current_user.get('Email') or ''
        contact = ''

        ok, msg = self.db.register_user_as_volunteer(self.current_user.get('Username'), event_id, fullname, email, contact)
        if ok:
            messagebox.showinfo("Registered", msg)
            self.refresh_all_data()
            self.refresh_public_portal()
        else:
            messagebox.showerror("Error", msg)

    def refresh_public_portal(self):
        """Refresh events list in public portal"""
        # Clear tree
        for item in self.public_events_tree.get_children():
            self.public_events_tree.delete(item)

        for e in self.db.events:
            venue = next((v for v in self.db.venues if v['Venue_id'] == e['Venue_id']), {})
            self.public_events_tree.insert('', tk.END, values=(
                e['Event_id'], e['Name'], e['Type'], e['Date'], e['Time'], venue.get('Name', '')
            ))
    
    def refresh_dashboard(self):
        """Refresh dashboard with latest data from database"""
        # Refresh data from database
        self.db.refresh_all_data()
        
        # Clear and recreate the dashboard
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        
        self.create_dashboard_tab()
        
        messagebox.showinfo("Success", "Dashboard refreshed with latest data!")
    
    def refresh_analytics(self):
        """Refresh all analytics reports with latest data"""
        # Report 1: Event Capacity Report
        self.report1_text.config(state=tk.NORMAL)
        self.report1_text.delete(1.0, tk.END)
        
        report1_content = "Event Name                    | Capacity | Available\n"
        report1_content += "-" * 60 + "\n"
        for event in self.db.events:
            venue = next((v for v in self.db.venues if v['Venue_id'] == event['Venue_id']), None)
            if venue:
                available = self.db.get_available_capacity(event['Event_id'])
                report1_content += f"{event['Name'][:30]:<30} | {venue['Capacity']:>8} | {available:>9}\n"
        
        self.report1_text.insert(tk.END, report1_content)
        self.report1_text.config(state=tk.DISABLED)
        
        # Report 2: Confirmed Participants
        self.report2_text.config(state=tk.NORMAL)
        self.report2_text.delete(1.0, tk.END)
        
        report2_content = "Participant Name     | Event Name                    | Status\n"
        report2_content += "-" * 70 + "\n"
        for ticket in self.db.tickets:
            if ticket['Status'] == 'Confirmed':
                participant = next((p for p in self.db.participants 
                                  if p['Participant_id'] == ticket['Participant_id']), None)
                event = next((e for e in self.db.events 
                            if e['Event_id'] == ticket['Event_id']), None)
                if participant and event:
                    report2_content += f"{participant['Name'][:20]:<20} | {event['Name'][:30]:<30} | {ticket['Status']}\n"
        
        self.report2_text.insert(tk.END, report2_content)
        self.report2_text.config(state=tk.DISABLED)
        
        # Report 3: Total Revenue by Organizer
        self.report3_text.config(state=tk.NORMAL)
        self.report3_text.delete(1.0, tk.END)
        
        report3_content = "Organizer Name              | Total Revenue\n"
        report3_content += "-" * 50 + "\n"
        
        organizer_revenue = {}
        for event in self.db.events:
            organizer = next((o for o in self.db.organizers 
                            if o['Organizer_id'] == event['Organizer_id']), None)
            if organizer:
                org_name = organizer['Name']
                if org_name not in organizer_revenue:
                    organizer_revenue[org_name] = 0
                
                # Calculate revenue for this event
                event_tickets = [t for t in self.db.tickets if t['Event_id'] == event['Event_id']]
                for ticket in event_tickets:
                    payment = next((p for p in self.db.payments 
                                  if p['Ticket_id'] == ticket['Ticket_id']), None)
                    if payment:
                        organizer_revenue[org_name] += payment['Amount']
        
        for org_name, revenue in organizer_revenue.items():
            report3_content += f"{org_name[:30]:<30} | ${revenue:>12,.2f}\n"
        
        self.report3_text.insert(tk.END, report3_content)
        self.report3_text.config(state=tk.DISABLED)
    
    # Event handler methods
    def filter_events(self, *args):
        """Filter events based on search text"""
        search_text = self.event_search_var.get().lower()
        
        # Clear tree
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        # Add filtered events
        for event in self.db.events:
            if search_text in event['Name'].lower() or search_text in event['Type'].lower():
                self.events_tree.insert('', tk.END, values=(
                    event['Event_id'],
                    event['Name'],
                    event['Type'],
                    event['Date'],
                    event['Time'],
                    event['Venue_id'],
                    event['Organizer_id']
                ))
    
    def add_event(self):
        """Add a new event"""
        # Get venue and organizer options
        venue_options = [f"{v['Venue_id']} - {v['Name']}" for v in self.db.venues]
        organizer_options = [f"{o['Organizer_id']} - {o['Name']}" for o in self.db.organizers]
        
        fields = [
            {'name': 'Event_id', 'label': 'Event ID', 'type': 'number'},
            {'name': 'Name', 'label': 'Event Name', 'type': 'text'},
            {'name': 'Type', 'label': 'Type', 'type': 'dropdown', 
             'values': ['Hackathon', 'Workshop', 'Party', 'Guest Lecture', 'Fun Activity']},
            {'name': 'Date', 'label': 'Date (YYYY-MM-DD)', 'type': 'date'},
            {'name': 'Time', 'label': 'Time (HH:MM:SS)', 'type': 'time'},
            {'name': 'Venue_id', 'label': 'Venue', 'type': 'dropdown', 'values': venue_options},
            {'name': 'Organizer_id', 'label': 'Organizer', 'type': 'dropdown', 'values': organizer_options}
        ]
        
        dialog = CRUDDialog(self.root, "Add Event", fields)
        self.root.wait_window(dialog)
        
        if dialog.result:
            # Extract IDs from dropdown selections
            dialog.result['Venue_id'] = int(dialog.result['Venue_id'].split(' - ')[0])
            dialog.result['Organizer_id'] = int(dialog.result['Organizer_id'].split(' - ')[0])
            
            # Add to database
            if self.db.add_event(dialog.result):
                self.refresh_events()
                messagebox.showinfo("Success", "Event added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add event to database")
    
    def edit_event(self):
        """Edit selected event"""
        selection = self.events_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an event to edit")
            return
        
        # Get selected event data
        item = self.events_tree.item(selection[0])
        event_id = item['values'][0]
        
        # Find event in database
        event = next((e for e in self.db.events if e['Event_id'] == event_id), None)
        if not event:
            return
        
        # Get venue and organizer options
        venue_options = [f"{v['Venue_id']} - {v['Name']}" for v in self.db.venues]
        organizer_options = [f"{o['Organizer_id']} - {o['Name']}" for o in self.db.organizers]
        
        fields = [
            {'name': 'Event_id', 'label': 'Event ID', 'type': 'number'},
            {'name': 'Name', 'label': 'Event Name', 'type': 'text'},
            {'name': 'Type', 'label': 'Type', 'type': 'dropdown', 
             'values': ['Hackathon', 'Workshop', 'Party', 'Guest Lecture', 'Fun Activity']},
            {'name': 'Date', 'label': 'Date (YYYY-MM-DD)', 'type': 'date'},
            {'name': 'Time', 'label': 'Time (HH:MM:SS)', 'type': 'time'},
            {'name': 'Venue_id', 'label': 'Venue', 'type': 'dropdown', 'values': venue_options},
            {'name': 'Organizer_id', 'label': 'Organizer', 'type': 'dropdown', 'values': organizer_options}
        ]
        
        # Prepare event data for dialog
        event_data = event.copy()
        event_data['Venue_id'] = f"{event['Venue_id']} - " + \
                                 next((v['Name'] for v in self.db.venues if v['Venue_id'] == event['Venue_id']), "")
        event_data['Organizer_id'] = f"{event['Organizer_id']} - " + \
                                     next((o['Name'] for o in self.db.organizers if o['Organizer_id'] == event['Organizer_id']), "")
        
        dialog = CRUDDialog(self.root, "Edit Event", fields, event_data)
        self.root.wait_window(dialog)
        
        if dialog.result:
            # Extract IDs from dropdown selections
            dialog.result['Venue_id'] = int(dialog.result['Venue_id'].split(' - ')[0])
            dialog.result['Organizer_id'] = int(dialog.result['Organizer_id'].split(' - ')[0])
            
            # Update in database
            if self.db.update_event(dialog.result):
                self.refresh_events()
                messagebox.showinfo("Success", "Event updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update event in database")
    
    def delete_event(self):
        """Delete selected event"""
        selection = self.events_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an event to delete")
            return
        
        item = self.events_tree.item(selection[0])
        event_id = item['values'][0]
        event_name = item['values'][1]
        
        # Check for related records
        tickets_count = sum(1 for t in self.db.tickets if t['Event_id'] == event_id)
        volunteers_count = sum(1 for v in self.db.volunteers if v['Event_id'] == event_id)
        sponsors_count = sum(1 for s in self.db.sponsors if s['Event_id'] == event_id)
        
        # Build confirmation message
        msg = f"Are you sure you want to delete event '{event_name}'?"
        if tickets_count > 0 or volunteers_count > 0 or sponsors_count > 0:
            msg += "\n\nThis will also delete:"
            if tickets_count > 0:
                msg += f"\n• {tickets_count} ticket(s) and their payment(s)"
            if volunteers_count > 0:
                msg += f"\n• {volunteers_count} volunteer(s)"
            if sponsors_count > 0:
                msg += f"\n• {sponsors_count} sponsor(s)"
        
        if messagebox.askyesno("Confirm Deletion", msg):
            # Delete event (database method handles cascading)
            if self.db.delete_event(event_id, event_name):
                # Refresh all related displays
                self.refresh_all_data()
                messagebox.showinfo("Success", 
                    f"Event '{event_name}' and all related records deleted successfully from database!")
            else:
                messagebox.showerror("Error", "Failed to delete event from database")
    
    def add_ticket(self):
        """Add a new ticket"""
        # Get event and participant options
        event_options = [f"{e['Event_id']} - {e['Name']}" for e in self.db.events]
        participant_options = [f"{p['Participant_id']} - {p['Name']}" for p in self.db.participants]
        
        fields = [
            {'name': 'Ticket_id', 'label': 'Ticket ID', 'type': 'number'},
            {'name': 'Event_id', 'label': 'Event', 'type': 'dropdown', 'values': event_options},
            {'name': 'Participant_id', 'label': 'Participant', 'type': 'dropdown', 'values': participant_options},
            {'name': 'Status', 'label': 'Status', 'type': 'dropdown', 
             'values': ['Pending', 'Confirmed', 'Cancelled']},
            {'name': 'Price', 'label': 'Price', 'type': 'number'}
        ]
        
        dialog = CRUDDialog(self.root, "Add Ticket", fields)
        self.root.wait_window(dialog)
        
        if dialog.result:
            # Extract IDs from dropdown selections
            dialog.result['Event_id'] = int(dialog.result['Event_id'].split(' - ')[0])
            dialog.result['Participant_id'] = int(dialog.result['Participant_id'].split(' - ')[0])
            
            # Trigger simulation: Check ticket price
            try:
                self.db.check_ticket_price(dialog.result['Price'])
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            
            # Check capacity before adding (simulating TR_CheckCapacityBeforeSale)
            available = self.db.get_available_capacity(dialog.result['Event_id'])
            if available <= 0 and dialog.result['Status'] == 'Confirmed':
                messagebox.showerror("Error", "Cannot add ticket: Event capacity is full!")
                return
            
            # Add to database
            if self.db.add_ticket(dialog.result):
                self.refresh_tickets()
                messagebox.showinfo("Success", "Ticket added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add ticket to database")
    
    def process_payment(self):
        """Process payment for a ticket"""
        ticket_id = self.payment_ticket_var.get()
        method = self.payment_method_var.get()
        amount = self.payment_amount_var.get()
        
        if not all([ticket_id, method, amount]):
            messagebox.showerror("Error", "Please fill all payment fields")
            return
        
        try:
            ticket_id = int(ticket_id)
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Invalid ticket ID or amount")
            return
        
        # Process payment
        result = self.db.confirm_payment(ticket_id, method, amount)
        messagebox.showinfo("Payment Result", result)
        
        # Clear fields
        self.payment_ticket_var.set("")
        self.payment_method_var.set("")
        self.payment_amount_var.set("")
        
        # Refresh displays
        self.refresh_tickets()
        self.refresh_payments()
    
    def add_participant(self):
        """Add a new participant"""
        fields = [
            {'name': 'Participant_id', 'label': 'Participant ID', 'type': 'number'},
            {'name': 'Name', 'label': 'Name', 'type': 'text'},
            {'name': 'Email', 'label': 'Email', 'type': 'text'},
            {'name': 'Contact', 'label': 'Contact', 'type': 'text'}
        ]
        
        dialog = CRUDDialog(self.root, "Add Participant", fields)
        self.root.wait_window(dialog)
        
        if dialog.result:
            # Check for duplicate email
            if any(p['Email'] == dialog.result['Email'] for p in self.db.participants):
                messagebox.showerror("Error", "Email already exists!")
                return
            
            if self.db.add_participant(dialog.result):
                self.refresh_participants()
                messagebox.showinfo("Success", "Participant added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add participant to database")
    
    def add_volunteer(self):
        """Add a new volunteer"""
        event_options = [f"{e['Event_id']} - {e['Name']}" for e in self.db.events]
        
        fields = [
            {'name': 'Volunteer_id', 'label': 'Volunteer ID', 'type': 'number'},
            {'name': 'Name', 'label': 'Name', 'type': 'text'},
            {'name': 'Email', 'label': 'Email', 'type': 'text'},
            {'name': 'Contact', 'label': 'Contact', 'type': 'text'},
            {'name': 'Type', 'label': 'Type', 'type': 'dropdown',
             'values': ['Registration Desk', 'Security', 'Stage Management', 'Logistics', 'Hospitality']},
            {'name': 'Event_id', 'label': 'Event', 'type': 'dropdown', 'values': event_options}
        ]
        
        dialog = CRUDDialog(self.root, "Add Volunteer", fields)
        self.root.wait_window(dialog)
        
        if dialog.result:
            # Extract Event ID
            dialog.result['Event_id'] = int(dialog.result['Event_id'].split(' - ')[0])
            
            # Check for duplicate email
            if any(v['Email'] == dialog.result['Email'] for v in self.db.volunteers):
                messagebox.showerror("Error", "Email already exists!")
                return
            
            if self.db.add_volunteer(dialog.result):
                self.refresh_volunteers()
                messagebox.showinfo("Success", "Volunteer added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add volunteer to database")
    
    def add_venue(self):
        """Add a new venue"""
        fields = [
            {'name': 'Venue_id', 'label': 'Venue ID', 'type': 'number'},
            {'name': 'Name', 'label': 'Name', 'type': 'text'},
            {'name': 'Location', 'label': 'Location', 'type': 'text'},
            {'name': 'Capacity', 'label': 'Capacity', 'type': 'number'}
        ]
        
        dialog = CRUDDialog(self.root, "Add Venue", fields)
        self.root.wait_window(dialog)
        
        if dialog.result:
            if dialog.result['Capacity'] <= 0:
                messagebox.showerror("Error", "Capacity must be greater than 0!")
                return
            
            if self.db.add_venue(dialog.result):
                self.refresh_venues()
                messagebox.showinfo("Success", "Venue added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add venue to database")
    
    def add_sponsor(self):
        """Add a new sponsor"""
        event_options = [f"{e['Event_id']} - {e['Name']}" for e in self.db.events]
        
        fields = [
            {'name': 'Sponsor_id', 'label': 'Sponsor ID', 'type': 'number'},
            {'name': 'Name', 'label': 'Sponsor Name', 'type': 'text'},
            {'name': 'Event_id', 'label': 'Event', 'type': 'dropdown', 'values': event_options},
            {'name': 'Contribution', 'label': 'Contribution', 'type': 'number'}
        ]
        
        dialog = CRUDDialog(self.root, "Add Sponsor", fields)
        self.root.wait_window(dialog)
        
        if dialog.result:
            # Extract Event ID
            dialog.result['Event_id'] = int(dialog.result['Event_id'].split(' - ')[0])
            
            if dialog.result['Contribution'] < 0:
                messagebox.showerror("Error", "Contribution cannot be negative!")
                return
            
            if self.db.add_sponsor(dialog.result):
                self.refresh_sponsors()
                messagebox.showinfo("Success", "Sponsor added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add sponsor to database")
            self.refresh_sponsors()
            messagebox.showinfo("Success", "Sponsor added successfully!")
    
    def check_capacity(self):
        """Check available capacity for an event"""
        event_options = [f"{e['Event_id']} - {e['Name']}" for e in self.db.events]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Check Event Capacity")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Select Event:", font=('Arial', 10)).pack(pady=10)
        
        event_var = tk.StringVar()
        event_combo = ttk.Combobox(dialog, textvariable=event_var, width=40)
        event_combo['values'] = event_options
        event_combo.pack(pady=5)
        
        result_label = ttk.Label(dialog, text="", font=('Arial', 12, 'bold'))
        result_label.pack(pady=20)
        
        def check():
            if event_var.get():
                event_id = int(event_var.get().split(' - ')[0])
                available = self.db.get_available_capacity(event_id)
                venue = next((v for v in self.db.venues 
                            for e in self.db.events 
                            if e['Event_id'] == event_id and e['Venue_id'] == v['Venue_id']), None)
                if venue:
                    result_label.config(text=f"Available Capacity: {available} / {venue['Capacity']}")
        
        check_btn = ttk.Button(dialog, text="Check Capacity", command=check)
        check_btn.pack(pady=10)
        
        close_btn = ttk.Button(dialog, text="Close", command=dialog.destroy)
        close_btn.pack()
    
    def export_reports(self):
        """Export all reports to a text file"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write("EVENT MANAGEMENT SYSTEM - REPORTS\n")
                f.write("=" * 80 + "\n\n")
                
                # Write all reports
                f.write("1. EVENT CAPACITY REPORT\n")
                f.write("-" * 40 + "\n")
                for event in self.db.events:
                    venue = next((v for v in self.db.venues if v['Venue_id'] == event['Venue_id']), None)
                    if venue:
                        available = self.db.get_available_capacity(event['Event_id'])
                        f.write(f"{event['Name']}: Capacity {venue['Capacity']}, Available {available}\n")
                
                f.write("\n2. TOTAL REVENUE BY ORGANIZER\n")
                f.write("-" * 40 + "\n")
                # Calculate and write revenue report
                
                f.write("\n3. SPONSORSHIP SUMMARY\n")
                f.write("-" * 40 + "\n")
                # Write sponsorship report
                
            messagebox.showinfo("Success", f"Reports exported to {filename}")
    
    # Refresh methods
    def refresh_all_data(self):
        """Refresh all data displays"""
        self.refresh_events()
        self.refresh_tickets()
        self.refresh_payments()
        self.refresh_participants()
        self.refresh_volunteers()
        self.refresh_venues()
        self.refresh_sponsors()
    
    def refresh_events(self):
        """Refresh events treeview"""
        # Clear tree
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        # Add all events
        for event in self.db.events:
            self.events_tree.insert('', tk.END, values=(
                event['Event_id'],
                event['Name'],
                event['Type'],
                event['Date'],
                event['Time'],
                event['Venue_id'],
                event['Organizer_id']
            ))
    
    def refresh_tickets(self):
        """Refresh tickets treeview"""
        # Clear tree
        for item in self.tickets_tree.get_children():
            self.tickets_tree.delete(item)
        
        # Add all tickets
        for ticket in self.db.tickets:
            # Color code based on status
            tag = ''
            if ticket['Status'] == 'Confirmed':
                tag = 'confirmed'
            elif ticket['Status'] == 'Pending':
                tag = 'pending'
            elif ticket['Status'] == 'Cancelled':
                tag = 'cancelled'
            
            self.tickets_tree.insert('', tk.END, values=(
                ticket['Ticket_id'],
                ticket['Event_id'],
                ticket['Participant_id'],
                ticket['Status'],
                f"${ticket['Price']:.2f}"
            ), tags=(tag,))
        
        # Configure tags
        self.tickets_tree.tag_configure('confirmed', foreground='green')
        self.tickets_tree.tag_configure('pending', foreground='orange')
        self.tickets_tree.tag_configure('cancelled', foreground='red')
        
        # Update payment ticket combo - show all pending tickets (regardless of payment status)
        pending_tickets = [str(t['Ticket_id']) for t in self.db.tickets if t['Status'] == 'Pending']
        if hasattr(self, 'payment_ticket_var'):
            ticket_combo = None
            for child in self.tickets_frame.winfo_children():
                if isinstance(child, ttk.PanedWindow):
                    for pane in child.winfo_children():
                        for widget in pane.winfo_children():
                            if isinstance(widget, ttk.LabelFrame):
                                for w in widget.winfo_children():
                                    if isinstance(w, ttk.Combobox):
                                        ticket_combo = w
                                        break
            if ticket_combo:
                ticket_combo['values'] = pending_tickets
    
    def refresh_payments(self):
        """Refresh payments treeview"""
        # Clear tree
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
        
        # Add all payments
        for payment in self.db.payments:
            self.payments_tree.insert('', tk.END, values=(
                payment['Payment_id'],
                payment['Ticket_id'],
                f"${payment['Amount']:.2f}",
                payment['Method'],
                payment['Date']
            ))
    
    def refresh_participants(self):
        """Refresh participants treeview"""
        # Clear tree
        for item in self.participants_tree.get_children():
            self.participants_tree.delete(item)
        
        # Add all participants
        for participant in self.db.participants:
            self.participants_tree.insert('', tk.END, values=(
                participant['Participant_id'],
                participant['Name'],
                participant['Email'],
                participant['Contact']
            ))
    
    def refresh_volunteers(self):
        """Refresh volunteers treeview"""
        # Clear tree
        for item in self.volunteers_tree.get_children():
            self.volunteers_tree.delete(item)
        
        # Add all volunteers
        for volunteer in self.db.volunteers:
            self.volunteers_tree.insert('', tk.END, values=(
                volunteer['Volunteer_id'],
                volunteer['Name'],
                volunteer['Email'],
                volunteer['Contact'],
                volunteer['Type'],
                volunteer['Event_id']
            ))
    
    def refresh_venues(self):
        """Refresh venues treeview"""
        # Clear tree
        for item in self.venues_tree.get_children():
            self.venues_tree.delete(item)
        
        # Add all venues
        for venue in self.db.venues:
            self.venues_tree.insert('', tk.END, values=(
                venue['Venue_id'],
                venue['Name'],
                venue['Location'],
                venue['Capacity']
            ))
    
    def refresh_sponsors(self):
        """Refresh sponsors treeview"""
        # Clear tree
        for item in self.sponsors_tree.get_children():
            self.sponsors_tree.delete(item)
        
        # Add all sponsors
        for sponsor in self.db.sponsors:
            self.sponsors_tree.insert('', tk.END, values=(
                sponsor['Sponsor_id'],
                sponsor['Name'],
                sponsor['Event_id'],
                f"${sponsor['Contribution']:.2f}"
            ))
        
        # Update total sponsorship
        total = sum(s['Contribution'] for s in self.db.sponsors)
        self.total_sponsorship_label.config(text=f"Total Sponsorship: ${total:,.2f}")
    
    def create_advanced_tab(self):
        """Create the advanced features tab with function calls and procedure testing"""
        main_frame = ttk.Frame(self.advanced_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Advanced Database Features", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Function Testing Section
        func_frame = ttk.LabelFrame(main_frame, text="Function Testing", padding=10)
        func_frame.pack(fill=tk.X, pady=10)
        
        # Available Capacity Function
        ttk.Label(func_frame, text="Check Available Capacity for Event:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.capacity_event_var = tk.StringVar()
        capacity_combo = ttk.Combobox(func_frame, textvariable=self.capacity_event_var, width=30)
        capacity_combo['values'] = [f"{e['Event_id']} - {e['Name']}" for e in self.db.events]
        capacity_combo.grid(row=0, column=1, pady=5, padx=5)
        
        capacity_btn = ttk.Button(func_frame, text="Check Capacity", 
                                 command=self.test_available_capacity)
        capacity_btn.grid(row=0, column=2, padx=5)
        
        self.capacity_result = ttk.Label(func_frame, text="", foreground=COLORS['primary'])
        self.capacity_result.grid(row=1, column=0, columnspan=3, pady=5, sticky=tk.W)
        
        # Confirmed Tickets Function
        ttk.Label(func_frame, text="Get Confirmed Tickets for Event:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.tickets_event_var = tk.StringVar()
        tickets_combo = ttk.Combobox(func_frame, textvariable=self.tickets_event_var, width=30)
        tickets_combo['values'] = [f"{e['Event_id']} - {e['Name']}" for e in self.db.events]
        tickets_combo.grid(row=2, column=1, pady=5, padx=5)
        
        tickets_btn = ttk.Button(func_frame, text="Get Count", 
                                command=self.test_confirmed_tickets)
        tickets_btn.grid(row=2, column=2, padx=5)
        
        self.tickets_result = ttk.Label(func_frame, text="", foreground=COLORS['primary'])
        self.tickets_result.grid(row=3, column=0, columnspan=3, pady=5, sticky=tk.W)
        
        # Get Organizer Name Function
        ttk.Label(func_frame, text="Get Organizer Name by ID:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.organizer_id_var = tk.StringVar()
        organizer_combo = ttk.Combobox(func_frame, textvariable=self.organizer_id_var, width=30)
        organizer_combo['values'] = [f"{o['Organizer_id']} - {o['Name']}" for o in self.db.organizers]
        organizer_combo.grid(row=4, column=1, pady=5, padx=5)
        
        organizer_btn = ttk.Button(func_frame, text="Get Name", 
                                  command=self.test_organizer_name)
        organizer_btn.grid(row=4, column=2, padx=5)
        
        self.organizer_result = ttk.Label(func_frame, text="", foreground=COLORS['primary'])
        self.organizer_result.grid(row=5, column=0, columnspan=3, pady=5, sticky=tk.W)
        
        # Procedure Testing Section
        proc_frame = ttk.LabelFrame(main_frame, text="Stored Procedure Testing", padding=10)
        proc_frame.pack(fill=tk.X, pady=10)
        
        # Get Event Summary
        ttk.Label(proc_frame, text="Get Event Summary:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.summary_event_var = tk.StringVar()
        summary_combo = ttk.Combobox(proc_frame, textvariable=self.summary_event_var, width=30)
        summary_combo['values'] = [f"{e['Event_id']} - {e['Name']}" for e in self.db.events]
        summary_combo.grid(row=0, column=1, pady=5, padx=5)
        
        summary_btn = ttk.Button(proc_frame, text="Get Summary", 
                                command=self.test_event_summary)
        summary_btn.grid(row=0, column=2, padx=5)
        
        self.summary_text = tk.Text(proc_frame, height=4, width=60)
        self.summary_text.grid(row=1, column=0, columnspan=3, pady=5, sticky=tk.W)
        
        # Mark Ticket as Pending
        ttk.Label(proc_frame, text="Mark Ticket as Pending:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.pending_ticket_var = tk.StringVar()
        pending_combo = ttk.Combobox(proc_frame, textvariable=self.pending_ticket_var, width=30)
        pending_combo['values'] = [f"{t['Ticket_id']} - Event {t['Event_id']} ({t['Status']})" for t in self.db.tickets]
        pending_combo.grid(row=2, column=1, pady=5, padx=5)
        
        pending_btn = ttk.Button(proc_frame, text="Mark Pending", 
                               command=self.test_mark_pending)
        pending_btn.grid(row=2, column=2, padx=5)
        
        # Trigger Information Section
        trigger_frame = ttk.LabelFrame(main_frame, text="Active Triggers Information", padding=10)
        trigger_frame.pack(fill=tk.X, pady=10)
        
        # Active Triggers Info
        trigger_info = """Active Triggers:

1. TR_CheckTicketPrice
   - Validates ticket price must be > 0 before insert
   - Triggered automatically when adding new tickets
   
2. TR_CheckCapacityBeforeSale
   - Validates venue capacity before ticket sale
   - Prevents overselling of event tickets
   
3. TR_UpdateVolunteerOnEventDelete
   - Logs event deletions to Log table
   - Triggered when an event is deleted"""
        
        info_label = ttk.Label(trigger_frame, text=trigger_info, justify=tk.LEFT, 
                             foreground=COLORS['text_secondary'], font=('Arial', 9))
        info_label.pack(pady=5, anchor=tk.W)
        
        # Logs Section
        log_frame = ttk.LabelFrame(main_frame, text="System Logs", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.logs_text = tk.Text(log_frame, height=8, width=80)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
        refresh_logs_btn = ttk.Button(log_frame, text="Refresh Logs", 
                                     command=self.refresh_logs)
        refresh_logs_btn.pack(pady=5)
    
    # Advanced feature handler methods
    def test_available_capacity(self):
        """Test the available capacity function"""
        if self.capacity_event_var.get():
            event_id = int(self.capacity_event_var.get().split(' - ')[0])
            available = self.db.get_available_capacity(event_id)
            event = next((e for e in self.db.events if e['Event_id'] == event_id), None)
            if event:
                venue = next((v for v in self.db.venues if v['Venue_id'] == event['Venue_id']), None)
                if venue:
                    self.capacity_result.config(
                        text=f"Available capacity for '{event['Name']}': {available} / {venue['Capacity']}"
                    )
        else:
            messagebox.showwarning("Warning", "Please select an event")

    def test_confirmed_tickets(self):
        """Test the confirmed tickets function"""
        if self.tickets_event_var.get():
            event_id = int(self.tickets_event_var.get().split(' - ')[0])
            count = self.db.get_total_confirmed_tickets(event_id)
            event = next((e for e in self.db.events if e['Event_id'] == event_id), None)
            if event:
                self.tickets_result.config(
                    text=f"Confirmed tickets for '{event['Name']}': {count}"
                )
        else:
            messagebox.showwarning("Warning", "Please select an event")
    
    def test_organizer_name(self):
        """Test the organizer name function"""
        if self.organizer_id_var.get():
            organizer_id = int(self.organizer_id_var.get().split(' - ')[0])
            organizer_name = self.db.get_organizer_name(organizer_id)
            self.organizer_result.config(
                text=f"Organizer Name: {organizer_name}"
            )
        else:
            messagebox.showwarning("Warning", "Please select an organizer")

    def test_event_summary(self):
        """Test the event summary procedure"""
        if self.summary_event_var.get():
            event_id = int(self.summary_event_var.get().split(' - ')[0])
            summary = self.db.get_event_summary(event_id)
            
            self.summary_text.delete(1.0, tk.END)
            if 'error' not in summary:
                self.summary_text.insert(tk.END, 
                                       f"Event: {summary['Event_Name']}\n"
                                       f"Venue: {summary['Venue_Name']}\n"
                                       f"Capacity: {summary['Capacity']}\n"
                                       f"Available: {summary['Available']}\n"
                                       f"Confirmed Tickets: {summary['Confirmed_Tickets']}")
            else:
                self.summary_text.insert(tk.END, f"Error: {summary['error']}")
        else:
            messagebox.showwarning("Warning", "Please select an event")
    
    def test_mark_pending(self):
        """Test the mark ticket as pending procedure"""
        if self.pending_ticket_var.get():
            ticket_id = int(self.pending_ticket_var.get().split(' - ')[0])
            result = self.db.mark_ticket_as_pending(ticket_id)
            messagebox.showinfo("Success", result)
            self.refresh_tickets()
            # Refresh the dropdown in the advanced tab
            for widget in self.advanced_frame.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame) and "Stored Procedure" in child.cget("text"):
                            for w in child.winfo_children():
                                if isinstance(w, ttk.Combobox):
                                    try:
                                        if 'Ticket' in str(w.cget('values')[0]) if w.cget('values') else False:
                                            w['values'] = [f"{t['Ticket_id']} - Event {t['Event_id']} ({t['Status']})" for t in self.db.tickets]
                                    except:
                                        pass
        else:
            messagebox.showwarning("Warning", "Please select a ticket")

    def refresh_logs(self):
        """Refresh the logs display"""
        self.logs_text.delete(1.0, tk.END)
        if self.db.logs:
            for log in reversed(self.db.logs[-10:]):  # Show last 10 logs
                self.logs_text.insert(tk.END, f"[{log['timestamp']}] {log['message']}\n")
        else:
            self.logs_text.insert(tk.END, "No logs available\n")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = EventManagementApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()