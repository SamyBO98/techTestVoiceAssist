import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app
from db import db, CallInfo
with app.app_context():
    calls = CallInfo.query.all()
    for c in calls:
        print(c)