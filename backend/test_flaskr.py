import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        
        self.host = "localhost:5432"
        self.user_name = "postgres"
        self.password = "12345"
        self.database_path = "postgres://{}:{}@{}/{}".format\
            (self.user_name, self.password, self.host, self.database_name)

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            "question": "This is question?",
            "answer": "this is answer.",
            "difficulty": 3,
            "category": 3
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        result = self.client().get('/categories')
        data = json.loads(result.data)

        self.assertEqual(result.status_code,200)
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        result = self.client().get('/questions')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_sent_invalid_page(self):
        result = self.client().get('/questions?page=20')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "resource not found")

    def test_delete_question(self):
        result = self.client().delete('/questions/10')
        data = json.loads(result.data)

        question = Question.query.filter(Question.id == 7).one_or_none()

        self.assertEqual(result.status_code,200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], 10)
        self.assertEqual(question, None)

    def test_422_sent_delete_invalid_question(self):
        result = self.client().delete('/questions/1000')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "unprocessable entity")

    def test_submit_question(self):
        result = self.client().post('/submit', json=self.new_question)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['success'])

    def test_search_not_found(self):
        result = self.client().post('/questions', json={"searchTerm": "NoBook"})
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)
    
    def test_get_list_category(self):
        result = self.client().get('/categories/2/questions')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['category'],2)
        self.assertTrue(len(data['questions']))
    
    def test_404_sent_invalid_category(self):
        result = self.client().get('/categories/10/questions')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "resource not found")

    def test_get_next_question(self):
        result = self.client().post('/quizzes', json={
            "previous_questions": [],
            "quiz_category": {"id": 0, "type": "All"}
        })
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertNotEqual(data['question'], None)

    def test_404_sent_invalid_quiz_category(self):
        result = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {'id': 10, 'type': "Medicine"}
        })
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "resource not found")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
