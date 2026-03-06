import sys
import os

# Add parent directory to path to import app and db modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from db import CallInfo

# Print all records stored in the database
with app.app_context():
    calls = CallInfo.query.all()
    for c in calls:
        print(c)
