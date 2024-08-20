import unittest
import requests
from faker import Faker


class PythonAPIs(unittest.TestCase):
    fake = Faker()
    baseUrl = "https://deployment.api-python.boilerplate.hng.tech"
    valid_body = {
        "email": "woss7@mailinator.com",
        "password": "Pa$$w0rd!",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
    existing_body = {
        "email": "woss5@mailinator.com",
        "password": "Pa$$w0rd!",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
    invalid_body = {
        "email": 12345678,
        "password": "Pa$$w0rd!",
        "first_name": 10110111,
        "last_name": fake.last_name(),
    }
    access_token = None
    user_id = None
    valid_body1 = {
        "email": fake.email(),
        "password": "Pa$$w0rd!",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
    valid_body2 = {
        "email": fake.email(),
        "password": "Pa$$w0rd!",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
    change_password = {"old_password": "Pa$$w0rd!", "new_password": "Pa$$w0rd!!"}
    VALID_CREDENTIALS = {
        "email": "woss1@mailinator.com",
        "password": "Pa$$w0rd!",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
    LOGIN_CREDENTIALS = {"email": "woss2@mailinator.com", "password": "Pa$$w0rd!"}
    INVALID_CREDENTIALS = {"username": "test@mail.com", "password": "wrongpassword"}
    create_profile = {
        "username": fake.user_name(),
        "pronouns": "It/is",
        "job_title": "Tester",
        "department": "Science",
        "social": "@me",
        "bio": fake.paragraph(),
        "phone_number": "+2348026653321",
        "avatar_url": fake.image_url(),
        "recovery_email": fake.email(),
    }

    @classmethod
    def setUpClass(cls):
        auth_response = requests.post(
            f"{cls.baseUrl}/api/v1/auth/login",
            json={"email": "woss2@mailinator.com", "password": "Pa$$w0rd!"},
        )
        auth_response_data = auth_response.json()
        cls.access_token = auth_response_data["data"]["access_token"]
        cls.user_id = auth_response_data["data"]["user"]["id"]
        print(auth_response_data)
        instance = cls()
        instance.assertEqual(
            auth_response.status_code,
            200,
            "Expected status code 200, got {}".format(auth_response.status_code),
        )

    def test_register_user_successfully(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/register", json=self.valid_body2
        )
        self.assertEqual(
            response.status_code,
            201,
            "Expected status code 201, got {}".format(response.status_code),
        )
        response_data = response.json()
        self.assertIn("access_token", response_data["data"])
        self.assertIsInstance(response_data["data"]["access_token"], str)
        self.assertGreater(len(response_data["data"]["access_token"]), 0)

    def test_register_with_invalid_credentials(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/register", json=self.invalid_body
        )
        self.assertEqual(
            response.status_code,
            422,
            "Expected status code 422, got {}".format(response.status_code),
        )
        response_data = response.json()

    def test_register_with_existing_credentials(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/register", json=self.existing_body
        )
        self.assertEqual(
            response.status_code,
            400,
            "Expected status code 400, got {}".format(response.status_code),
        )
        response_data = response.json()

    def test_token_expiry(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/register", json=self.valid_body1
        )
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        access_token = response_data["data"]["access_token"]
        import jwt

        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        self.assertIn("exp", decoded_token)
        self.assertGreater(decoded_token["exp"], 0)

    def test_register_admin_successfully(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/register-super-admin", json=self.valid_body
        )
        self.assertEqual(
            response.status_code,
            201,
            "Expected status code 201, got {}".format(response.status_code),
        )
        response_data = response.json()
        self.assertIn("access_token", response_data["data"])
        self.assertIsInstance(response_data["data"]["access_token"], str)
        self.assertGreater(len(response_data["data"]["access_token"]), 0)
        print(
            "Super Admin successfully created, status code is {}".format(
                response.status_code
            )
        )

    def test_register_admin_with_invalid_credentials(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/register-super-admin", json=self.invalid_body
        )
        self.assertEqual(
            response.status_code,
            422,
            "Expected status code 422, got {}".format(response.status_code),
        )

    def test_register_admin_with_existing_credentials(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/register-super-admin", json=self.existing_body
        )
        self.assertEqual(
            response.status_code,
            400,
            "Expected status code 400, got {}".format(response.status_code),
        )

    def test_refresh_token(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/refresh-access-token", headers=headers
        )
        self.assertEqual(
            response.status_code,
            200,
            "Expected status code 200, got {}".format(response.status_code),
        )

    def test_logout(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.post(f"{self.baseUrl}/api/v1/auth/logout", headers=headers)
        self.assertEqual(
            response.status_code,
            200,
            "Expected status code 200, got {}".format(response.status_code),
        )

    def test_refresh_token(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/refresh-access-token", headers=headers
        )
        self.assertEqual(
            response.status_code,
            200,
            "Expected status code 200, got {}".format(response.status_code),
        )

    def test_send_token(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/request-token",
            json={"email": "woss@mailinator.com"},
        )
        self.assertEqual(
            response.status_code,
            200,
            "Expected status code 200, got {}".format(response.status_code),
        )

    def test_login_with_token(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/verify-token",
            json={"email": "woss@mailinator.com", "token": "123456"},
        )
        self.assertEqual(
            response.status_code,
            200,
            "Expected status code 200, got {}".format(response.status_code),
        )

    def test_request_magicLink(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/request-magic-link",
            json={"email": "woss@mailinator.com"},
        )
        self.assertEqual(
            response.status_code,
            200,
            "Expected status code 200, got {}".format(response.status_code),
        )

    def test_facebook_login(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/facebook-login",
            json={"token": self.access_token},
        )
        self.assertEqual(
            response.status_code,
            200,
            "Expected status code 200, got {}".format(response.status_code),
        )

    def test_newsletter(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/newsletters", json={"email": "woss@mailinator.com"}
        )
        self.assertEqual(
            response.status_code,
            200,
            "Expected status code 200, got {}".format(response.status_code),
        )

    def test_change_password(self):
        response = requests.patch(
            f"{self.baseUrl}/api/v1/users/me/password", json=self.change_password
        )
        self.assertEqual(
            response.status_code,
            200,
            "Expected status code 200, got {}".format(response.status_code),
        )

    def register_user(self):
        response = requests.post(
            f"{self.baseUrl}/api/v1/auth/register-super-admin",
            json=self.VALID_CREDENTIALS,
        )
        self.assertEqual(response.status_code, 201)
        response_data = response.json()

    def test_get_endpoint(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{self.baseUrl}/api/v1/auth/admin", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello, admin!"})

    def test_get_auth_google_redirect_success(self):
        response = requests.get(f"{self.baseUrl}/api/v1/auth/google")
        self.assertEqual(response.status_code, 200)

    def test_get_current_user_details(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{self.baseUrl}/api/v1/users/me", headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_get_user_by_id(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(
            f"{self.baseUrl}/api/v1/users/{self.user_id}", headers=headers
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_user_by_id(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.delete(
            f"{self.baseUrl}/api/v1/users/{self.user_id}", headers=headers
        )
        self.assertEqual(response.status_code, 204)

    def test_get_current_user_profile(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(
            f"{self.baseUrl}/api/v1/profile/current-user", headers=headers
        )
        self.assertEqual(response.status_code, 200)

    def test_create_profile(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.patch(
            f"{self.baseUrl}/api/v1/users/me/password",
            json=self.change_password,
            headers=headers,
        )
        self.assertEqual(
            response.status_code,
            200,
            "Expected status code 200, got {}".format(response.status_code),
        )

    def test_get_all_organisation_billing(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(
            f"{self.baseUrl}/api/v1/organisation/billing-plans", headers=headers
        )
        self.assertEqual(response.status_code, 200)
