# tests/conftest.py
import sys
import os
from dotenv import load_dotenv

# Add the root directory of the project to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from the .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
