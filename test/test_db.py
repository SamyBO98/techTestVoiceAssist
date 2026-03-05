import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from db import CallInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#Create DB
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "calls_info.db"))
engine = create_engine(f"sqlite:///{DB_FILE}", echo=True)

#Create table if doesnt exist
CallInfo.metadata.create_all(engine)

#Create a session to make tests
Session = sessionmaker(bind=engine)

#Create session that closes automatically
with Session() as session:
    # Add test
    new_call = CallInfo(call_id="testID", appointment_date="2026-03-06")
    session.add(new_call)
    session.commit()

    # Print all results
    all_calls = session.query(CallInfo).all()
    for call in all_calls:
        print(call)