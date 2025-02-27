"""
Environment Variable Validator

This module provides validation for environment variables without modifying
existing code in main.py or settings.py. It should be imported at the beginning
of the application startup process.
"""
import os
import sys
from typing import Dict, List, Any, Optional, Tuple


class EnvValidator:
    # Class variable to define variable categories for template generation
    CATEGORIES = {
        "Core Settings": [
            "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES", "JWT_REFRESH_EXPIRY",
            "APP_URL", "PYTHON_ENV", "MY_NEW_VARIABLE"
        ],
        "Database Settings": [
            "DB_TYPE", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT",
            "MYSQL_DRIVER", "DB_URL"
        ],
        "OAuth Settings": [
            "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "FRONTEND_URL"
        ],
        "Email Settings": [
            "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_FROM", "MAIL_PORT", "MAIL_SERVER",
            "MAILJET_API_KEY", "MAILJET_API_SECRET"
        ],
        "SMS Settings": [
            "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"
        ],
        "Payment Settings": [
            "FLUTTERWAVE_SECRET", "PAYSTACK_SECRET", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"
        ],
        "Testing": [
            "TESTING"
        ]
    }

    def __init__(self):
        self.required_vars = {
            # Core settings
            "SECRET_KEY": {"required": True, "min_length": 16, "description": "Secret key for cryptographic signing"},
            "ALGORITHM": {"required": True, "default": "HS256", "description": "JWT algorithm"},
            "ACCESS_TOKEN_EXPIRE_MINUTES": {"required": True, "type": "int", "default": "3000",
                                            "description": "Access token expiry time in minutes"},
            "JWT_REFRESH_EXPIRY": {"required": True, "type": "int", "default": "7",
                                   "description": "Refresh token expiry time in days"},
            "MY_NEW_VARIABLE": {
                "required": True,  # or False
                "description": "Description of what this variable does",
                # Optional: add any other validation rules
                "default": "12345678",  # if applicable
                "type": "int",  # if applicable
                "min_length": 8,  # if applicable
                "allowed_values": ["12345678", "87654321"]
            },


            # Database settings
            "DB_TYPE": {"required": True, "allowed_values": ["postgresql", "mysql", "sqlite"], "default": "postgresql",
                        "description": "Database type"},
            "DB_NAME": {"required": True, "description": "Database name"},
            "DB_USER": {"required": True, "description": "Database username"},
            "DB_PASSWORD": {"required": True, "description": "Database password"},
            "DB_HOST": {"required": True, "description": "Database host"},
            "DB_PORT": {"required": True, "type": "int", "default": "5432", "description": "Database port"},

            # OAuth settings
            "GOOGLE_CLIENT_ID": {"required": False, "description": "Google OAuth client ID"},
            "GOOGLE_CLIENT_SECRET": {"required": False, "description": "Google OAuth client secret"},
            "FRONTEND_URL": {"required": False, "default": "http://127.0.0.1:3000/login-success",
                             "description": "Frontend URL for OAuth redirects"},

            # Email settings
            "MAIL_USERNAME": {"required": True, "description": "SMTP username"},
            "MAIL_PASSWORD": {"required": True, "description": "SMTP password"},
            "MAIL_FROM": {"required": True, "description": "Sender email address"},
            "MAIL_PORT": {"required": True, "type": "int", "default": "465", "description": "SMTP port"},
            "MAIL_SERVER": {"required": True, "description": "SMTP server"},

            # SMS settings
            "TWILIO_ACCOUNT_SID": {"required": False, "description": "Twilio account SID"},
            "TWILIO_AUTH_TOKEN": {"required": False, "description": "Twilio authentication token"},
            "TWILIO_PHONE_NUMBER": {"required": False, "description": "Twilio phone number"},

            # Payment settings
            "FLUTTERWAVE_SECRET": {"required": False, "description": "Flutterwave API secret key"},
            "PAYSTACK_SECRET": {"required": False, "description": "Paystack API secret key"},
            "STRIPE_SECRET_KEY": {"required": False, "description": "Stripe secret key"},
            "STRIPE_WEBHOOK_SECRET": {"required": False, "description": "Stripe webhook secret"},

            # MailJet settings
            "MAILJET_API_KEY": {"required": False, "description": "MailJet API key"},
            "MAILJET_API_SECRET": {"required": False, "description": "MailJet API secret"},

            # Environment settings
            "PYTHON_ENV": {"required": False, "allowed_values": ["dev", "test", "prod"], "default": "dev",
                           "description": "Application environment"},
        }

        # Keep track of validation issues
        self.validation_errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """
        Validates all required environment variables.

        Returns:
            bool: True if all required variables are valid, False otherwise
        """
        self.validation_errors = []
        self.warnings = []

        # Check all required environment variables
        for var_name, requirements in self.required_vars.items():
            value = os.environ.get(var_name)

            # Skip non-required variables that aren't set
            if not requirements.get("required", False) and value is None:
                continue

            # For required variables, ensure they are set
            if requirements.get("required", False) and (value is None or value.strip() == ""):
                # Check if there's a default value
                if "default" in requirements:
                    self.warnings.append(f"{var_name} is using default value: {requirements['default']}")
                else:
                    self.validation_errors.append(f"{var_name} is required but not set")
                    continue

            # Only validate if the value is actually set
            if value is not None and value.strip() != "":
                # Type validation
                if requirements.get("type") == "int":
                    try:
                        int(value)
                    except ValueError:
                        self.validation_errors.append(f"{var_name} must be an integer")

                # Length validation
                if "min_length" in requirements and len(value) < requirements["min_length"]:
                    self.validation_errors.append(
                        f"{var_name} must be at least {requirements['min_length']} characters long"
                    )

                # Value validation
                if "allowed_values" in requirements and value.lower() not in requirements["allowed_values"]:
                    self.validation_errors.append(
                        f"{var_name} must be one of: {', '.join(requirements['allowed_values'])}"
                    )

        return len(self.validation_errors) == 0

    def print_validation_results(self) -> None:
        """Prints validation results to the console."""
        if not self.validation_errors and not self.warnings:
            print("\033[92m✓ All environment variables are valid\033[0m")
            return

        if self.warnings:
            print("\033[93m! Warnings:\033[0m")
            for warning in self.warnings:
                print(f"\033[93m  - {warning}\033[0m")

        if self.validation_errors:
            print("\033[91m✗ Validation errors:\033[0m")
            for error in self.validation_errors:
                print(f"\033[91m  - {error}\033[0m")

            print("\n\033[93mPlease check your .env file and set all required variables.\033[0m")
            print("\033[93mRun 'python create_env_template.py' to generate a template.\033[0m")

    def validate_or_exit(self) -> None:
        """Validates all environment variables and exits if validation fails."""
        if not self.validate_all():
            self.print_validation_results()
            sys.exit(1)
        else:
            # Just print warnings if any
            if self.warnings:
                self.print_validation_results()

    def add_variable(self, name: str, config: dict, category: Optional[str] = None) -> None:
        """
        Add a new environment variable to the validator.

        Args:
            name: The environment variable name
            config: Dictionary with validation configuration
            category: Optional category name for template organization
        """
        # Add to required_vars dictionary
        self.required_vars[name] = config

        # Add to appropriate category if specified
        if category and category in self.CATEGORIES and name not in self.CATEGORIES[category]:
            self.CATEGORIES[category].append(name)


def generate_env_template() -> None:
    """Generates a .env.template file with all required variables."""
    validator = EnvValidator()

    lines = ["# Environment Variables Template", "# ============================", ""]

    for category, var_names in validator.CATEGORIES.items():
        lines.append(f"# {category}")
        for var_name in var_names:
            var_config = validator.required_vars.get(var_name, {})
            comment = f"# {var_config.get('description', '')}"

            if var_config.get("required", False):
                comment += " (Required)"

            if "default" in var_config:
                value = var_config["default"]
                lines.append(f"{comment}")
                lines.append(f"{var_name}={value}")
            else:
                value = ""
                lines.append(f"{comment}")
                lines.append(f"{var_name}={value}")

            lines.append("")

    # Write to file
    env_template_path = ".env.template"
    with open(env_template_path, "w") as f:
        f.write("\n".join(lines))

    print(f".env.template created at {os.path.abspath(env_template_path)}")
    print("Copy this file to .env and fill in the required values.")


def generate_clean_env_file() -> None:
    """
    Generates a clean .env file from the template that's compatible
    with python-dotenv parser.
    """
    validator = EnvValidator()

    lines = []

    for category, var_names in validator.CATEGORIES.items():
        lines.append(f"# {category}")
        for var_name in var_names:
            var_config = validator.required_vars.get(var_name, {})

            # Add the variable name with its default value if available
            if "default" in var_config:
                value = var_config["default"]
                lines.append(f"{var_name}={value}")
            else:
                lines.append(f"{var_name}=")

        # Add a blank line between categories
        lines.append("")

    # Write to file
    env_path = ".env"
    with open(env_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Clean .env file created at {os.path.abspath(env_path)}")
    print("Please fill in the required values.")


# Function to call at application startup
def validate_environment() -> None:
    """Validates environment variables at application startup."""
    validator = EnvValidator()
    validator.validate_or_exit()


if __name__ == "__main__":
    # If the script is run directly, generate both files
    generate_env_template()
    generate_clean_env_file()