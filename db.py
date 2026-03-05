import sqlite3

#Name of the DB
DB_NAME = "voiceAssist.db"


#DB initialization
def init_db():
    #Connect to DB (if file doesnt exist it will be automatically created by SQLite)
    conn = sqlite3.connect(DB_NAME)
    #Allow us to exec command
    c = conn.cursor()
    #Create the table call_end_info
    #ID primary key that increments each time
    #Appointment date in Text (no Date type in SQLite)
    c.execute("""
        CREATE TABLE IF NOT EXISTS call_end_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_date TEXT
        )
    """)
    #Validate all changes
    conn.commit()
    #Close DB connexion
    conn.close()

#Update DB (Insert)
def save_appointment(appointment_date: str):
    #Connexion to our DB
    conn = sqlite3.connect(DB_NAME)
    #Allow us to exec command
    c = conn.cursor()
    #Insert in our table (more secure with placeholder)
    c.execute("INSERT INTO call_end_info (appointment_date) VALUES (?)", (appointment_date,))
    #Validate all changes
    conn.commit()
    #Close DB connexion
    conn.close()