"""
Environment Variable Validation Plugin
"""
import os
import sys
from pathlib import Path

# Find the root directory
current_dir = Path(__file__).resolve().parent
root_dir = current_dir
# Add any logic here to find your project root if needed

# Add the root directory to the Python path
sys.path.insert(0, str(root_dir))

# Import the validator
try:
    from env_validator import validate_environment

    # Run validation
    validate_environment()
except ImportError:
    print("\033[93mWarning: Environment validator not found.\033[0m")
    print("\033[93mMake sure env_validator.py is in your project root.\033[0m")
    # Don't exit, allow the application to continue
except Exception as e:
    print(f"\033[91mError validating environment variables: {str(e)}\033[0m")
    if os.environ.get("PYTHON_ENV") != "prod":
        print("\033[93mContinuing despite validation errors (non-production environment).\033[0m")
    else:
        print("\033[91mExiting due to validation errors in production environment.\033[0m")
        sys.exit(1)