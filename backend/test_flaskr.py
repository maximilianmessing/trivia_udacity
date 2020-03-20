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
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {'question': 'Where is x',
                             'answer': 'it is in Y',
                             'difficulty': 1,
                             'category': 2}
        self.new_invalid_question = {'question': 'Where is x',
                                     'answer': 'it is in Y',
                                     'difficulty': 1,
                                     'category': "I am not an integer"}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertEqual(len(data['categories']), 6)

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], len(Question.query.all()))
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(len(data['categories']), len(Category.query.all()))
        self.assertIsNone(data['current_category'])

    def test_get_questions_out_of_page_range(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource was not found")

    def test_delete_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 2)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(len(Question.query.all()), 19)
        self.assertIsNone(Question.query.filter(
            Question.id == 2).one_or_none())

    def test_delete_404_if_question_does_not_exist(self):
        res = self.client().delete('/questions/200')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource was not found")

    def test_create_new_question(self):
        res = self.client().post(
            '/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 20)
        self.assertGreater(len(data['questions']), 0)

    def test_create_new_invalid_question_yields_422(self):
        res = self.client().post(
            '/questions', json=self.new_invalid_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Unprocessable entity")

    def test_search_for_question(self):
        res = self.client().post('/questions', json={'searchTerm': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 2)
        self.assertEqual(data['total_questions'], 2)
        self.assertIsNone(data['current_category'])

    def test_get_questions_for_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(len(data['categories']), len(Category.query.all()))
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['current_category'], 1)

    def test_get_questions_for_outofbounce_category_404(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource was not found")


# Testing post quizzes previous question (id11) in category has to yield id 10 as current question-

    def test_post_quizzes(self):
        res = self.client().post(
            '/quizzes', json={"previous_questions":[11],"quiz_category":{"type":"Sports","id":"6"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['question']), 5)
        self.assertEqual(data['question']['id'], 10)

    def test_post_quizzes_all_category(self):
        res = self.client().post(
            '/quizzes', json={"previous_questions":[],"quiz_category":{"type":"click","id":0}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['question']), 5)

    def test_post_quizzes_outofbounce_category_404(self):
        res = self.client().post(
            '/quizzes', json={"previous_questions":[],"quiz_category":{"type":"Fantasy","id":300}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource was not found")

    def test_delete_quizzes_405(self):
        res = self.client().delete('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Method not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
