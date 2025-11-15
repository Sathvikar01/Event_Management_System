# Event Management System

A comprehensive desktop application for managing events, participants, tickets, payments, and more using Python and MySQL.

## 📋 Features

- **Event Management**: Create, view, update, and delete events with venue and organizer details
- **Participant Management**: Register participants with contact information
- **Ticket System**: Issue tickets with status tracking (Confirmed, Pending, Cancelled)
- **Payment Processing**: Record and track payments with multiple payment methods
- **Venue Management**: Manage venues with capacity tracking
- **Organizer Management**: Track event organizers and their contact details
- **Sponsor Management**: Record sponsor contributions for events
- **Volunteer Management**: Coordinate volunteers for different events
- **Reports & Analytics**:
  - Event capacity analysis
  - Revenue reporting by organizer
  - Sponsorship summaries
  - Participant attendance tracking
- **Database Persistence**: Auto-export to SQL file after each operation
- **Cascading Deletes**: Automatic cleanup of related records
- **Logging System**: Track all database operations

## 🛠️ Technology Stack

- **Frontend**: Python Tkinter (GUI)
- **Backend**: Python 3.x
- **Database**: MySQL 8.0
- **Connector**: mysql-connector-python

## 📦 Installation

### Prerequisites

1. **Python 3.7+** - [Download Python](https://www.python.org/downloads/)
2. **MySQL Server 8.0+** - [Download MySQL](https://dev.mysql.com/downloads/mysql/)

### Setup Steps

1. **Clone the repository** (or download the files):
   ```bash
   git clone <repository-url>
   cd dbms
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

If you see linting errors in your editor such as "Import 'mysql.connector' could not be resolved" (Pylance), make sure you created and activated your virtual environment before installing packages. Example for PowerShell:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If the editor still reports the error after installing, reload your editor or ensure the Python interpreter is set to use the `.venv` interpreter.

4. **Configure database connection**:
   - Open `db_config.py`
   - Update with your MySQL credentials:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'database': 'Event_Management_DB',
       'user': 'root',
       'password': 'your_password'
   }
   ```

5. **Initialize the database**:
   ```bash
   mysql -u root -p < dbms.sql
   ```
   Or run in PowerShell:
   ```powershell
   $env:MYSQL_PWD="your_password" ; & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -e "source dbms.sql"
   ```

6. **Run the application**:
   ```bash
   python main.py
   ```

## 🗂️ Project Structure

```
dbms/
├── main.py              # Main application with GUI
├── db_config.py         # Database configuration
├── dbms.sql            # Database schema and data
├── requirements.txt     # Python dependencies
├── setup_database.py    # Database setup utility (optional)
├── setup_log_table.py   # Log table setup (optional)
└── README.md           # This file
```

## 💾 Database Schema

The system includes the following tables:

- **organizer**: Event organizers with contact details
- **venue**: Event venues with location and capacity
- **event**: Events with type, date, time, venue, and organizer
- **participants**: Event participants/attendees
- **ticket**: Ticket sales with status and pricing
- **payment**: Payment records with methods and amounts
- **sponsor**: Sponsor contributions for events
- **volunteers**: Volunteer assignments for events
- **log**: System operation logs

### Key Features:

- **Stored Procedures**:
  - `SP_ConfirmPayment`: Process payments and confirm tickets
  - `SP_MarkTicketAsPending`: Update ticket status
  - `SP_GetEventSummary`: Get event details with venue info

- **Functions**:
  - `FN_GetAvailableCapacity`: Calculate available seats
  - `FN_GetTotalConfirmedTickets`: Count confirmed tickets
  - `FN_GetOrganizerName`: Retrieve organizer name

- **Triggers**:
  - `TR_CheckCapacityBeforeSale`: Prevent overselling tickets
  - `TR_CheckTicketPrice`: Validate ticket prices
  - `TR_UpdateVolunteerOnEventDelete`: Log event deletions

## 🚀 Usage

### Running the Application

1. Start the application:
   ```bash
   python main.py
   ```

2. The main window displays tabs for:
   - Events
   - Participants
   - Tickets
   - Payments
   - Venues
   - Organizers
   - Sponsors
   - Volunteers
   - Reports
   - Logs

### Common Operations

#### Adding an Event
1. Go to the "Events" tab
2. Click "Add Event"
3. Fill in event details (name, type, date, time)
4. Select venue and organizer
5. Click "Save"

#### Registering a Participant
1. Go to the "Participants" tab
2. Click "Add Participant"
3. Enter name, email, and contact
4. Click "Save"

#### Registering as a Volunteer (Guest Login)
1. From the "Events" tab choose an event and click "Register as Volunteer"
2. Log in or create a guest account when prompted
3. Pick a volunteer domain from the radio list
4. Click the **Confirm** button to submit the selection (Cancel returns to the event list)

#### Issuing a Ticket
1. Go to the "Tickets" tab
2. Click "Add Ticket"
3. Select event and participant
4. Set price and status
5. Click "Save"

#### Processing Payment
1. Go to the "Payments" tab
2. Click "Add Payment"
3. Select ticket
4. Enter amount and payment method
5. Click "Save"

#### Viewing Reports
1. Go to the "Reports" tab
2. Select report type:
   - Event Capacity Report
   - Revenue by Organizer
   - Sponsorship Summary
3. View results in the display area

## 🔧 Configuration

### Database Configuration
Edit `db_config.py` to match your MySQL setup:
```python
DB_CONFIG = {
    'host': 'localhost',      # Database host
    'database': 'Event_Management_DB',  # Database name
    'user': 'root',           # MySQL username
    'password': 'your_pass'   # MySQL password
}
```

### Auto-Export Feature
The application automatically exports the database to `dbms.sql` after each operation. This can be disabled in `main.py` if needed.

## 🐛 Troubleshooting

### Connection Issues
- Verify MySQL is running: `mysql --version`
- Check credentials in `db_config.py`
- Ensure database exists: `SHOW DATABASES;`

### Import Errors
- Install missing packages: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.7+)

### GUI Issues
- Ensure Tkinter is installed (usually included with Python)
- On Linux: `sudo apt-get install python3-tk`
- Volunteer dialog missing buttons? Update to the latest code; the confirm/cancel row now renders below the scrollable domain list so you can finalize the selection.
- Duplicate volunteer email errors? The app now auto-applies plus-addressing (e.g., `guest+ev1014@example.com`) when the same person signs up for multiple events so registrations succeed without schema changes.

## 📝 License

This project is for educational purposes.

## 👥 Contributors

- Event Management Team

## 📞 Support

For issues or questions, please create an issue in the repository or contact the development team.

---

**Last Updated**: November 2025
