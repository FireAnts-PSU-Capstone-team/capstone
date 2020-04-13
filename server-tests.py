import json
import unittest
from io import BytesIO

import db.connection as db_connection
from server import app
from flask_sqlalchemy import SQLAlchemy

# initialize sql-alchemy
sql_alchemy = SQLAlchemy()
sql_alchemy.init_app(app)


class TestServerApp(unittest.TestCase):
    """Api tests"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client
        self.cur, self.conn = db_connection.pg_connect()
        self.nonsense = 'asdfgh'
        with open('resources/sample-row-1.json') as f:
            self.sample_row = json.load(f)

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            sql_alchemy.create_all()

    def get_intake(self):
        return self.client().get('/list?table=intake')

    def test_api_can_get_intake_table(self):
        """Api should get all data (GET)."""
        response = self.get_intake()
        self.assertEqual(response.status_code, 200)

    def test_api_can_add_row(self):
        """Api should add data to a table (PUT)."""
        # Add some data
        response = self.client().put('/load?table=intake', data=self.sample_row, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Check that data is added
        # response = self.get_intake()
        # self.assertEqual(response.status_code, 200)
        # self.assertIn("Marion's Holdings, LTD.", str(response.data))

    # def test_api_can_upload_file(self):
    #     """API should post file and process it if correctly formatted (POST)."""
    #     # Don't know about this one yet, not sure how posting the file works
    #     with open('files/sample.xlsx', 'rb') as f:
    #         file_data = f.read()
    #     response = self.client().post('/load',
    #                                   buffered=True,
    #                                   data={'file': (BytesIO(file_data), 'files/sample.xlsx')},
    #                                   content_type='multipart/form-data')
    #     self.assertEqual(response.status_code, 200)
    #
    #     # Check whether data posted
    #     response = self.get_intake()
    #     self.assertIn("New Horizons Consultants, LLC", str(response.data))
    #
    # def test_api_can_reject_missing_data_when_adding(self):
    #     """Api should reject when user attempts to add data with missing fields. (PUT)"""
    #     invalid_sample = self.sample_row
    #     del invalid_sample['DBA']
    #     invalid_sample['Entity'] = self.nonsense
    #     response = self.client().put('/load?table=intake', data=invalid_sample)
    #     self.assertEqual(response.status_code, 400)
    #
    #     # Check that data hasn't been added
    #     getResponse = self.get_intake()
    #     self.assertEqual(response.status_code, 200)
    #     self.assertNotIn(self.nonsense, str(getResponse.data))
    #
    # def test_api_can_reject_invalid_data_when_adding(self):
    #     """Api should reject when user attempts to add data with invalid fields. (POST)"""
    #     invalid_sample = self.sample_row
    #     invalid_sample['Extraneous'] = 'true'
    #     invalid_sample['DBA'] = self.nonsense
    #     response = self.client().put('/load?table=intake', data=invalid_sample)
    #     self.assertEqual(response.status_code, 400)
    #
    #     # Check that data hasn't been added
    #     getResponse = self.get_intake()
    #     self.assertEqual(response.status_code, 200)
    #     self.assertNotIn(self.nonsense, str(getResponse.data))
    #
    # def test_api_can_reject_empty_data_when_adding(self):
    #     """Api should reject when user attempts to add empty data. (POST)"""
    #     response = self.client().post('/load')
    #     self.assertEqual(response.status_code, 400)

    # Not functionality we're implementing, at least yet

    # def test_api_can_edit_data(self):
    #     """Api should edit data (PUT)"""
    #     # Add some data to be edited
    #     addResponse = self.client().post('/cannabisdb/', data=self.sample_row)
    #     self.assertEqual(addResponse.status_code, 200)
    #
    #     # Edit this newly added data
    #     new_data = {'firstname': 'Jane', 'lastname': 'Smith', 'city': 'Kampala'}
    #     editResponse = self.client().put('/cannabisdb/1', data=new_data)
    #     self.assertEqual(editResponse.status_code, 200)
    #
    #     # Check if data is edited
    #     getResponse = self.client().get('/cannabisdb/')
    #     self.assertEqual(getResponse.status_code, 200)
    #     self.assertIn('Kampala', str(getResponse.data))
    #
    # def test_api_can_reject_empty_data_when_editing(self):
    #     """Api should reject when user attempts to edit data with empty data. (PUT)"""
    #     # Add some data to be editted
    #     addResponse = self.client().post('/load?take=intake', data=self.sample_data)
    #     self.assertEqual(addResponse.status_code, 200)
    #
    #     # Edit this newly added data with nothing, should fail
    #     editResponse = self.client().put('/cannabisdb/1')
    #     self.assertEqual(editResponse.status_code, 400)
    #
    #     # Check that data has not been edited
    #     getResponse = self.client().get('/cannabisdb/')
    #     self.assertEqual(getResponse.status_code, 200)
    #     self.assertIn('Pyongyang', str(getResponse.data))
    #
    # def test_api_can_reject_missing_data_when_editing(self):
    #     """Api should reject when user attempts to edit data with data that has missing fields. (PUT)"""
    #     # Add some data to be editted
    #     addResponse = self.client().post('/cannabisdb/', data=self.sample_data)
    #     self.assertEqual(addResponse.status_code, 200)
    #
    #     # Edit this newly added data with missing data
    #     new_data = {'firstname': 'Jane', 'lastname': 'Smith'}
    #     editResponse = self.client().put('/cannabisdb/1', data=new_data)
    #     self.assertEqual(editResponse.status_code, 400)
    #
    #     # Check that data has not been edited
    #     getResponse = self.client().get('/cannabisdb/')
    #     self.assertEqual(getResponse.status_code, 200)
    #     self.assertIn('Pyongyang', str(getResponse.data))
    #
    # def test_api_can_reject_invalid_data_when_editing(self):
    #     """Api should reject when user attempts to edit data with data that has invalid fields. (PUT)"""
    #     # Add some data to be editted
    #     addResponse = self.client().post('/cannabisdb/', data=self.sample_data)
    #     self.assertEqual(addResponse.status_code, 200)
    #
    #     # Edit this newly added data with invalid data
    #     new_data = {'first': 'Jane'}
    #     editResponse = self.client().put('/cannabisdb/1', data=new_data)
    #     self.assertEqual(editResponse.status_code, 400)
    #
    #     # Check that data has not been edited
    #     getResponse = self.client().get('/cannabisdb/')
    #     self.assertEqual(getResponse.status_code, 200)
    #     self.assertIn('Pyongyang', str(getResponse.data))
    #
    # def test_api_can_delete_data(self):
    #     """Api should delete existing data. (DELETE)"""
    #     # Add some data to be deleted
    #     addResponse = self.client().post('/cannabisdb/', data=self.sample_data)
    #     self.assertEqual(addResponse.status_code, 200)
    #
    #     # Delete this newly added data
    #     deleteResponse = self.client().delete('/cannabisdb/1')
    #     self.assertEqual(deleteResponse.status_code, 200)
    #
    #     # Check if data has been deleted
    #     getResponse = self.client().get('/cannabisdb/')
    #     self.assertEqual(getResponse.status_code, 200)
    #     self.assertNotIn('Pyongyang', str(getResponse.data))
    #
    # def test_api_can_reject_nonexistent_data_when_deleting(self):
    #     """Api should reject when user attempts to delete data that does not exist. (DELETE)"""
    #     # Delete some data that should not exist
    #     deleteResponse = self.client().delete('/cannabisdb/999')
    #     self.assertEqual(deleteResponse.status_code, 400)

        # Edit this newly added data
        new_data = {'firstname': 'Jane', 'lastname': 'Smith', 'city': 'Kampala'}
        editResponse = self.client().put('/cannabisdb/1', data=new_data)
        self.assertEqual(editResponse.status_code, 200)

        # Check if data is editted
        getResponse = self.client().get('/cannabisdb/')
        self.assertEqual(getResponse.status_code, 200)
        self.assertIn('Kampala', str(getResponse.data))

    def test_api_can_reject_empty_data_when_editing(self):
        """Api should reject when user attempts to edit data with empty data. (PUT)"""
        # Add some data to be editted
        addResponse = self.client().post('/cannabisdb/', data=self.data)
        self.assertEqual(addResponse.status_code, 200)

        # Edit this newly added data with nothing, should fail
        editResponse = self.client().put('/cannabisdb/1')
        self.assertEqual(editResponse.status_code, 400)

        # Check that data has not been edited
        getResponse = self.client().get('/cannabisdb/')
        self.assertEqual(getResponse.status_code, 200)
        self.assertIn('Pyongyang', str(getResponse.data))

    def test_api_can_reject_missing_data_when_editing(self):
        """Api should reject when user attempts to edit data with data that has missing fields. (PUT)"""
        # Add some data to be editted
        addResponse = self.client().post('/cannabisdb/', data=self.data)
        self.assertEqual(addResponse.status_code, 200)

        # Edit this newly added data with missing data
        new_data = {'firstname': 'Jane', 'lastname': 'Smith'}
        editResponse = self.client().put('/cannabisdb/1', data=new_data)
        self.assertEqual(editResponse.status_code, 400)

        # Check that data has not been edited
        getResponse = self.client().get('/cannabisdb/')
        self.assertEqual(getResponse.status_code, 200)
        self.assertIn('Pyongyang', str(getResponse.data))

    def test_api_can_reject_invalid_data_when_editing(self):
        """Api should reject when user attempts to edit data with data that has invalid fields. (PUT)"""
        # Add some data to be editted
        addResponse = self.client().post('/cannabisdb/', data=self.data)
        self.assertEqual(addResponse.status_code, 200)

        # Edit this newly added data with invalid data
        new_data = {'first': 'Jane'}
        editResponse = self.client().put('/cannabisdb/1', data=new_data)
        self.assertEqual(editResponse.status_code, 400)

        # Check that data has not been edited
        getResponse = self.client().get('/cannabisdb/')
        self.assertEqual(getResponse.status_code, 200)
        self.assertIn('Pyongyang', str(getResponse.data))

    def tearDown(self):
        """teardown all initialized variables."""
        db_connection.pg_disconnect(self.cur, self.conn)

        with self.app.app_context():
            # drop all tables
            sql_alchemy.session.remove()
            sql_alchemy.drop_all()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
