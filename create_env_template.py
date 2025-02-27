"""
Generate a template .env file with all required environment variables.

This script creates a .env.template file that includes all required and
optional environment variables with descriptions.
"""
from env_validator import generate_env_template

if __name__ == "__main__":
    generate_env_template()