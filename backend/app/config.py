"""
Support Ticket Automation System
Application Configuration
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration
# Can be overridden via DATABASE_URL environment variable
DEFAULT_SQLITE_PATH = BASE_DIR / "support_tickets.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")

# Application metadata
APP_NAME = "Support Ticket Automation System"
APP_VERSION = "1.0.0"
API_PREFIX = "/api"

# CORS configuration
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]
