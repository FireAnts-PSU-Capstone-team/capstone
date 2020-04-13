import json
import unittest
import server
import Connection
from flask_sqlalchemy import SQLAlchemy

# initialize sql-alchemy
db = SQLAlchemy()

class TestServerApp(unittest.TestCase):
    """Api tests"""

    def setUp(self):
        """Define test variables and initialize app."""
        super().setUp()
        # TODO: AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
        # Connection.pgSQLconnect()
        self.app = server.app
        self.client = self.app.test_client
        self.sample_data = {'firstname': 'John', 'lastname': 'Doe', 'city': 'Pyongyang'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_api_can_get_all_data(self):
        """Api should get all data (GET)."""
        response = self.client().get('/cannabisdb/')
        self.assertEqual(response.status_code, 200)

    def test_api_can_add_data(self):
        """Api should add data to a table (POST)."""
        response = self.client().post('/cannabisdb/', data=self.data)
        self.assertEqual(response.status_code, 200)

    def test_api_can_reject_missing_data_when_adding(self):
        """Api should reject when user attempts to add data with missing fields. (POST)"""
        response = self.client().post('cannabisdb/', data={'firstname': 'John'})
        self.assertEqual(response.status_code, 400)

    def test_api_can_reject_invalid_data_when_adding(self):
        """Api should reject when user attempts to add data with invalid fields. (POST)"""
        response = self.client().post('/cannabisdb/', data={'first': 'John'})
        self.assertEqual(response.status_code, 400)

    def test_api_can_reject_empty_data_when_adding(self):
        """Api should reject when user attempts to add empty data. (POST)"""
        response = self.client().post('/cannabisdb/')
        self.assertEqual(response.status_code, 400)

    def test_api_can_edit_data(self):
        """Api should edit data (PUT)"""
        addResponse = self.client().post('/cannabisdb/', data=self.data)
        self.assertEqual(addResponse.status_code, 200)

    def tearDown(self):
        """teardown all initialized variables."""
        # TODO: AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
        super().tearDown()
        Connection.pgSqlDisconnect()

        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
