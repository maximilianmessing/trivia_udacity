import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins.
  Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"*": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE')
        return response
    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    def formatted_categories():
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type
        return formatted_categories

    @app.route('/categories')
    def categories():
        categories = formatted_categories()
        return jsonify({"success": True,
                        "categories": categories})

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom
of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    def pagination_questions(selection, request):
        page = request.args.get('page', 1, type=int)
        start = QUESTIONS_PER_PAGE * (page - 1)
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        return questions[start:end]

    @app.route('/questions')
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = pagination_questions(selection, request)
        categories = formatted_categories()
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': categories,
            'current_category': None,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
        })

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question
  the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        if question is None:
            abort(404)
        try:
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = pagination_questions(selection, request)
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except Exception:
            abort(422)

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=["POST"])
    def create_new_question():
        body = request.get_json()

        search_term = body.get('searchTerm', None)
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        if search_term is None:
            try:
                question = Question(question=new_question,
                                    answer=new_answer,
                                    difficulty=new_difficulty,
                                    category=new_category)
                question.insert()
                selection = Question.query.order_by(Question.id).all()
                current_questions = pagination_questions(selection, request)
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
            except Exception:
                abort(422)
        else:
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            current_questions = pagination_questions(selection, request)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(current_questions),
                'current_category': None,
            })

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_for_category(category_id):
        selection = Question.query.filter(
            Question.category == category_id).order_by(Question.id)
        current_questions = pagination_questions(selection, request)
        categories = formatted_categories()
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': categories,
            'current_category': category_id,
            'total_questions': len(selection.all())
        })
    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def get_quizz_question():
        body = request.get_json()
        quiz_category = body.get('quiz_category', None).get('id')
        previous_questions = body.get('previous_questions', None)

        if quiz_category == 0:
            possible_questions = Question.query.filter(
                Question.id.notin_(previous_questions))
        else:
            possible_questions = Question.query.filter(
                Question.category == quiz_category).filter(
                Question.id.notin_(previous_questions))
        possible_questions_ids = [x.id for x in possible_questions.all()]
        if possible_questions_ids == []:
            abort(404)

        next_question_id = random.choice(possible_questions_ids)

        next_question = Question.query.filter(
            Question.id == next_question_id).one_or_none().format()
        return jsonify({
            'success': True,
            'question': next_question
        })

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            "error": 404,
            "message": "Resource was not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            "error": 422,
            "message": "Unprocessable entity"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success': False,
            "error": 405,
            "message": "Method not found"
        }), 405

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            'success': False,
            "error": 500,
            "message": "Internal Server error"
        }), 500

    return app
