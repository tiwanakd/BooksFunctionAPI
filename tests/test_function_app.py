import json
from unittest.mock import MagicMock, patch
from azure.functions import HttpRequest, HttpResponse
import unittest

from function_app import get_all_books, get_books_by_genre
from summary_fuction import generate_book_summary

class TestFunction(unittest.TestCase):
            
    def test_get_all_books(self):
        # Mock HttpRequest
        mock_request = HttpRequest(
            method='GET',
            body=None,
            url='/allbooks'
        )

        # Mock DocumentList
        mock_document_list = [
            MagicMock(to_json=lambda: '{"title": "Book", "author": "Author", "genre": "Genre", \
                      "publication_year": 2024, "coverURL": "https://booksapistorage.blob.core.windows.net/books-cover-images/Book.jpg"}')
        ]

        # Call the function
        func_call = get_all_books.build().get_user_function()
        response = func_call(mock_request, mock_document_list)

        #Checking the status code for request
    
        self.assertEqual(response.status_code,200)

        # Check if the function returns an HttpResponse
        self.assertIsInstance(response, HttpResponse)

        # Parse the response body
        response_data = json.loads(response.get_body())

        # Check the items in the response_data
        self.assertEqual(response_data[0]['title'],'Book')
        self.assertEqual(response_data[0]['author'],'Author')
        self.assertEqual(response_data[0]['genre'],'Genre')
        self.assertEqual(response_data[0]['publication_year'],2024)
        self.assertEqual(response_data[0]['coverURL'],'https://booksapistorage.blob.core.windows.net/books-cover-images/Book.jpg')

    def test_get_books_by_genre(self):

        genre_name = 'Fiction'

        #Mock Request
        mock_request = HttpRequest(
            method='GET',
            body=None,
            url='booksbygenre/{genre_name}}',
            route_params={'genre_name':genre_name}
        )

        # Mock DocumentList
        mock_document_list = [
            MagicMock(to_json=lambda: '{"title": "Book", "author": "Author", "genre": "Fiction", \
                      "publication_year": 2024, "coverURL": "https://booksapistorage.blob.core.windows.net/books-cover-images/Book.jpg"}'),
            MagicMock(to_json=lambda: '{"title": "Book2", "author": "Author2", "genre": "Fiction", \
            "publication_year": 2024, "coverURL": "https://booksapistorage.blob.core.windows.net/books-cover-images/Book2.jpg"}')
        ]

        func_call = get_books_by_genre.build().get_user_function()
        response = func_call(mock_request, mock_document_list)

        self.assertEqual(response.status_code,200)
        self.assertIsInstance(response, HttpResponse)

        response_data = json.loads(response.get_body())

        #Check if the Genere name is same for all the books retuened
        assert all(book.get('genre') == genre_name for book in response_data)

    def test_generate_book_summary(self):
        # Mock HttpRequest with a book_name parameter
        book_name = 'Atomic Habits'
        mock_request = HttpRequest(
            method='GET',
            body=None,
            url=f'summary/{book_name}',
            route_params={'book_name': book_name}
        )

        # Mock DocumentList
        mock_document_list = [
            MagicMock(to_json=lambda: '{"title": "Atomic Habits", "author": "James Clear", "genre": "Self-Help", \
                      "publication_year": 2018, "coverURL": "https://booksapistorage.blob.core.windows.net/books-cover-images/AtomicHabits.jpg"}')
        ]

        # Mock OpenAI API response
        with patch('summary_fuction.OpenAI') as mock_openai:
            mock_openai_instance = mock_openai.return_value
            mock_openai_instance.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='A summary of The Atomic Habits.'))])

            # Call the function
            func_call = generate_book_summary.build().get_user_function()
            response = func_call(mock_request, mock_document_list)

        # Check if the function returns an HttpResponse
        self.assertIsInstance(response, HttpResponse)

        # Parse the response body
        response_data = json.loads(response.get_body())

        # Check if the response_data contains the book information and the generated summary
        self.assertIn('title', response_data)
        self.assertIn('author',response_data)
        self.assertIn('genre', response_data)
        self.assertIn('publication_year', response_data)
        self.assertIn('coverURL', response_data)
        self.assertIn('generatedSummary',response_data)




