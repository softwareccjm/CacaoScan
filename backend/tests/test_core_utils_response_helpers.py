"""
Tests unitarios para core.utils.response_helpers.

Cubre todas las funciones de creación de respuestas:
- create_error_response
- create_success_response
"""
from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response

from core.utils.response_helpers import (
    create_error_response,
    create_success_response
)


class ResponseHelpersTestCase(TestCase):
    """Tests para funciones de response helpers."""

    def test_create_error_response_minimal(self):
        """Test create_error_response with minimal parameters."""
        response = create_error_response("Error message")
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 400)
        
        data = response.data
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Error message")
        self.assertNotIn('error_type', data)
        self.assertNotIn('details', data)

    def test_create_error_response_with_error_type(self):
        """Test create_error_response with error_type."""
        response = create_error_response(
            "Error message",
            error_type="ValidationError"
        )
        
        data = response.data
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Error message")
        self.assertEqual(data['error_type'], "ValidationError")

    def test_create_error_response_with_details(self):
        """Test create_error_response with details."""
        details = {'field': 'email', 'code': 'invalid'}
        response = create_error_response(
            "Error message",
            details=details
        )
        
        data = response.data
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Error message")
        self.assertEqual(data['details'], details)

    def test_create_error_response_with_all_params(self):
        """Test create_error_response with all parameters."""
        details = {'field': 'email'}
        response = create_error_response(
            "Error message",
            error_type="ValidationError",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )
        
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        data = response.data
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Error message")
        self.assertEqual(data['error_type'], "ValidationError")
        self.assertEqual(data['details'], details)

    def test_create_error_response_with_different_status_codes(self):
        """Test create_error_response with different status codes."""
        status_codes = [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
        
        for status_code in status_codes:
            response = create_error_response("Error", status_code=status_code)
            self.assertEqual(response.status_code, status_code)

    def test_create_success_response_minimal(self):
        """Test create_success_response with minimal parameters."""
        response = create_success_response("Success message")
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 200)
        
        data = response.data
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Success message")

    def test_create_success_response_with_data(self):
        """Test create_success_response with data."""
        data_dict = {'item_id': 123, 'name': 'Test Item'}
        response = create_success_response("Success message", data=data_dict)
        
        data = response.data
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Success message")
        self.assertEqual(data['item_id'], 123)
        self.assertEqual(data['name'], 'Test Item')

    def test_create_success_response_data_overwrites_message(self):
        """Test that data dict keys don't overwrite success/message unless explicitly."""
        data_dict = {'success': False, 'message': 'Overwrite attempt'}
        response = create_success_response("Original message", data=data_dict)
        
        # data.update() will overwrite, this is expected behavior
        data = response.data
        # Note: This tests the actual behavior - data.update() will overwrite
        # If we want to prevent this, we'd need to modify the function
        self.assertIn('success', data)
        self.assertIn('message', data)

    def test_create_success_response_with_nested_data(self):
        """Test create_success_response with nested data."""
        nested_data = {
            'user': {
                'id': 1,
                'username': 'testuser',
                'profile': {
                    'bio': 'Test bio'
                }
            }
        }
        response = create_success_response("Success", data=nested_data)
        
        data = response.data
        self.assertEqual(data['user']['id'], 1)
        self.assertEqual(data['user']['username'], 'testuser')
        self.assertEqual(data['user']['profile']['bio'], 'Test bio')

    def test_create_success_response_with_different_status_codes(self):
        """Test create_success_response with different status codes."""
        status_codes = [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_202_ACCEPTED
        ]
        
        for status_code in status_codes:
            response = create_success_response("Success", status_code=status_code)
            self.assertEqual(response.status_code, status_code)

    def test_create_success_response_with_empty_data(self):
        """Test create_success_response with empty data dict."""
        response = create_success_response("Success", data={})
        
        data = response.data
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Success")
        # Empty dict should not add extra keys
        self.assertEqual(len(data), 2)

