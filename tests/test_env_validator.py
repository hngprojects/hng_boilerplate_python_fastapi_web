import os
import pytest
import sys
from unittest.mock import patch, MagicMock

# Import the module to test
from env_validator import EnvValidator, validate_environment


class TestEnvValidator:
    def setup_method(self):
        """Setup method for tests."""
        # Create a fresh validator for each test
        self.validator = EnvValidator()

        # Backup existing environment variables and clear for test
        self.env_backup = os.environ.copy()
        os.environ.clear()

    def teardown_method(self):
        """Teardown method for tests."""
        # Restore environment variables
        os.environ.clear()
        os.environ.update(self.env_backup)

    def test_init(self):
        """Test the initialization of EnvValidator."""
        assert isinstance(self.validator.required_vars, dict)
        assert len(self.validator.required_vars) > 0
        assert len(self.validator.validation_errors) == 0
        assert len(self.validator.warnings) == 0

    def test_validate_all_success(self):
        """Test validation with all required variables set."""
        # Set all required variables in the environment
        for var_name, req in self.validator.required_vars.items():
            if req.get("required", False):
                if "default" in req:
                    os.environ[var_name] = req["default"]
                elif "min_length" in req:
                    os.environ[var_name] = "x" * req["min_length"]
                elif "allowed_values" in req and req["allowed_values"]:
                    os.environ[var_name] = req["allowed_values"][0]
                elif req.get("type") == "int":
                    os.environ[var_name] = "123"
                else:
                    os.environ[var_name] = "test_value"

        # Run validation
        result = self.validator.validate_all()

        # Check results
        assert result is True
        assert len(self.validator.validation_errors) == 0

    def test_validate_all_missing_required(self):
        """Test validation with missing required variables."""
        # Leave environment empty to ensure required variables are missing

        # Run validation
        result = self.validator.validate_all()

        # Check results
        assert result is False
        assert len(self.validator.validation_errors) > 0

        # Check for expected error messages
        for var_name, req in self.validator.required_vars.items():
            if req.get("required", False) and "default" not in req:
                expected_error = f"{var_name} is required but not set"
                assert any(expected_error in error for error in self.validator.validation_errors)

    def test_validate_default_values(self):
        """Test validation with default values."""
        # Run validation with empty environment
        self.validator.validate_all()

        # Check if warnings for defaults are generated
        for var_name, req in self.validator.required_vars.items():
            if req.get("required", False) and "default" in req:
                expected_warning = f"{var_name} is using default value: {req['default']}"
                assert any(expected_warning in warning for warning in self.validator.warnings)

    def test_validate_type_int(self):
        """Test validation of integer type variables."""
        # Find an integer variable
        int_vars = [var_name for var_name, req in self.validator.required_vars.items()
                    if req.get("type") == "int" and req.get("required", False)]

        if not int_vars:
            pytest.skip("No integer type variables to test")

        var_name = int_vars[0]

        # Test with valid integer
        os.environ[var_name] = "123"
        self.validator.validate_all()
        error_message = f"{var_name} must be an integer"
        assert not any(error_message in error for error in self.validator.validation_errors)

        # Test with invalid integer
        os.environ[var_name] = "not_an_integer"
        self.validator.validate_all()
        assert any(error_message in error for error in self.validator.validation_errors)

    def test_validate_min_length(self):
        """Test validation of minimum length requirement."""
        # Find a variable with min_length
        min_length_vars = [var_name for var_name, req in self.validator.required_vars.items()
                           if "min_length" in req and req.get("required", False)]

        if not min_length_vars:
            pytest.skip("No min_length variables to test")

        var_name = min_length_vars[0]
        min_length = self.validator.required_vars[var_name]["min_length"]

        # Test with valid length
        os.environ[var_name] = "x" * min_length
        self.validator.validate_all()
        error_message = f"{var_name} must be at least {min_length} characters long"
        assert not any(error_message in error for error in self.validator.validation_errors)

        # Test with invalid length
        os.environ[var_name] = "x" * (min_length - 1)
        self.validator.validate_all()
        assert any(error_message in error for error in self.validator.validation_errors)

    def test_validate_allowed_values(self):
        """Test validation of allowed values."""
        # Find a variable with allowed_values
        allowed_values_vars = [var_name for var_name, req in self.validator.required_vars.items()
                               if "allowed_values" in req and req.get("required", False)]

        if not allowed_values_vars:
            pytest.skip("No allowed_values variables to test")

        var_name = allowed_values_vars[0]
        allowed_values = self.validator.required_vars[var_name]["allowed_values"]

        # Test with valid value
        os.environ[var_name] = allowed_values[0]
        self.validator.validate_all()
        error_message = f"{var_name} must be one of: {', '.join(allowed_values)}"
        assert not any(error_message in error for error in self.validator.validation_errors)

        # Test with invalid value
        os.environ[var_name] = "invalid_value"
        self.validator.validate_all()
        assert any(error_message in error for error in self.validator.validation_errors)

    def test_print_validation_results_success(self):
        """Test printing validation results with success."""
        # Mock print function
        with patch('builtins.print') as mock_print:
            # Simulate successful validation
            self.validator.validation_errors = []
            self.validator.warnings = []

            # Call the method
            self.validator.print_validation_results()

            # Verify output
            mock_print.assert_called_once_with("\033[92m✓ All environment variables are valid\033[0m")

    def test_print_validation_results_warnings(self):
        """Test printing validation results with warnings."""
        # Mock print function
        with patch('builtins.print') as mock_print:
            # Simulate warnings
            self.validator.validation_errors = []
            self.validator.warnings = ["Warning 1", "Warning 2"]

            # Call the method
            self.validator.print_validation_results()

            # Verify output
            assert mock_print.call_count >= 3
            mock_print.assert_any_call("\033[93m! Warnings:\033[0m")

    def test_print_validation_results_errors(self):
        """Test printing validation results with errors."""
        # Mock print function
        with patch('builtins.print') as mock_print:
            # Simulate errors
            self.validator.validation_errors = ["Error 1", "Error 2"]
            self.validator.warnings = []

            # Call the method
            self.validator.print_validation_results()

            # Verify output
            assert mock_print.call_count >= 3
            mock_print.assert_any_call("\033[91m✗ Validation errors:\033[0m")

    def test_validate_or_exit_success(self):
        """Test validate_or_exit with successful validation."""
        # Mock validate_all to return True
        with patch.object(self.validator, 'validate_all', return_value=True), \
                patch.object(self.validator, 'print_validation_results') as mock_print:
            # Call the method
            self.validator.validate_or_exit()

            # Verify behavior
            mock_print.assert_not_called()

    def test_validate_or_exit_with_warnings(self):
        """Test validate_or_exit with warnings."""
        # Mock validate_all to return True but with warnings
        with patch.object(self.validator, 'validate_all', return_value=True), \
                patch.object(self.validator, 'print_validation_results') as mock_print:
            # Set warnings
            self.validator.warnings = ["Warning"]

            # Call the method
            self.validator.validate_or_exit()

            # Verify behavior
            mock_print.assert_called_once()

    @patch('sys.exit')
    def test_validate_or_exit_failure(self, mock_exit):
        """Test validate_or_exit with validation failure."""
        # Mock validate_all to return False
        with patch.object(self.validator, 'validate_all', return_value=False), \
                patch.object(self.validator, 'print_validation_results') as mock_print:
            # Call the method
            self.validator.validate_or_exit()

            # Verify behavior
            mock_print.assert_called_once()
            mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    def test_validate_environment(self, mock_exit):
        """Test the validate_environment function."""
        # Mock EnvValidator
        with patch('env_validator.EnvValidator') as MockValidator:
            # Setup mock validator
            mock_validator = MagicMock()
            MockValidator.return_value = mock_validator

            # Call function
            validate_environment()

            # Verify behavior
            MockValidator.assert_called_once()
            mock_validator.validate_or_exit.assert_called_once()


# Additional test for template generation
class TestEnvTemplateGeneration:
    @patch('builtins.open', new_callable=MagicMock)
    @patch('os.path.abspath', return_value='/path/to/.env.template')
    @patch('builtins.print')
    def test_generate_env_template(self, mock_print, mock_abspath, mock_open):
        """Test generating the environment template."""
        from env_validator import generate_env_template

        # Setup mock for file write
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Call function
        generate_env_template()

        # Verify file was written to
        mock_open.assert_called_once_with(".env.template", "w")
        assert mock_file.write.call_count == 1

        # Verify output messages
        mock_print.assert_any_call(".env.template created at /path/to/.env.template")
        mock_print.assert_any_call("Copy this file to .env and fill in the required values.")