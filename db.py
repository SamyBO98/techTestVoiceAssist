from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------------------------
# DB CONNECTION NOTE
#
# For simple tests or low usage, opening and closing a session per script run 
# works fine. In a web app (e.g., Flask), it's better to use one session per 
# HTTP request or a connection pool. SQLAlchemy manages this automatically in Flask.
# ---------------------------------------------------------------------------------

db = SQLAlchemy()
TABLE_NAME = "calls_info"

class CallInfo(db.Model):
    __tablename__ = TABLE_NAME
    #ID that will increment automatically (Integer type + our primary key)
    id = db.Column(db.Integer, primary_key=True)
    #index=True -> can search by call_id faster
    call_id = db.Column(db.String(128), index=True)
    appointment_date = db.Column(db.String(128), nullable=False)
    creation_date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(ZoneInfo("Europe/Paris")),
        nullable=False
    )
    #db.Column(db.Integer, default=lambda: int(datetime.now(ZoneInfo("Europe/Paris")).timestamp()))

    #return a printable representation of the object
    def __repr__(self) -> str:
        return ("id= " + str(self.id) + " | call_id= " + str(self.call_id) +  " | appointment_date= " + str(self.appointment_date)+ " | creation_date= " + str(self.creation_date))