"""
Configuration module for loading environment variables.

This module loads environment variables from the .env file and validates
required settings before the application starts.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Define the path to the .env file (one directory up from this file)
env_path = Path(__file__).parent.parent / ".env"

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

# Database Configuration
# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate that DATABASE_URL is not empty
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found in environment variables. "
        "Please create a .env file with DATABASE_URL or set it in your environment. "
        "See .env.example for the required format."
    )

# JWT Authentication Configuration
# Get JWT_SECRET_KEY from environment (required for Stage 2+)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Get JWT_ALGORITHM from environment (defaults to HS256)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Get Better Auth public key URL (optional - for production JWT validation)
BETTER_AUTH_PUBLIC_KEY_URL = os.getenv("BETTER_AUTH_PUBLIC_KEY_URL")

# Validate JWT configuration if needed
# Note: JWT_SECRET_KEY validation can be added when API endpoints are implemented
# For now, allow it to be None during database-only usage (Stage 1)
