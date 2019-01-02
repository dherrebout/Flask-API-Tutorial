import datetime
from flask import Flask, jsonify, request, Response
import json
import jwt
import settings
import test


books = [
    {
        'name': 'The Book',
        'price': 7.99,
        'isbn': 9823748230
    },
    {
        'name': 'The cat in the hat',
        'price': 6.99,
        'isbn': 9823748231
    }
]

DEFAULT_PAGE_LIMIT = 3

app = Flask(__name__)

app.config['SECRET_KEY'] = 'meow'


@app.route('/login') 
def get_token():
    expiration_date = (datetime.datetime.utcnow() +
                       datetime.timedelta(seconds=100))
    token = jwt.encode({'exp': expiration_date},
                       app.config['SECRET_KEY'], algorithm='HS256')
    return token


# GET /books
@app.route('/books')
def get_books():
    token = request.args.get('token')
    try:
        jwt.decode(token, app.config['SECRET_KEY'])
    except:
        return jsonify({'error': 'Need a valid token to view this page'}), 401
    return jsonify({'books': books})


# Check validity
def validBookObject(bookObject):
    if ("name" in bookObject and
            "price" in bookObject and
            "isbn" in bookObject):
        return True
    else:
        return False


# POST /books
@app.route('/books', methods=['POST'])
def add_book():
    request_data = request.get_json()
    if(validBookObject(request_data)):
        new_book = {
            "name": request_data['name'],
            "price": request_data['price'],
            "isbn": request_data['isbn']
        }
        books.insert(0, new_book)
        response = Response("", status=201, mimetype='application/json')
        response.headers['Location'] = "/books/" + str(new_book['isbn'])
        return response
    else:
        invalidBookObjectErrorMsg = {
            "error": "Invalid book object passed in the request",
            "helpString": "Data passed in similar to this " +
            "{'name': 'bookname', 'price: '7.99', 'isbn': 92839823}"
        }
        response = Response(json.dumps(invalidBookObjectErrorMsg),
                            status=400, mimetype='applicaton/json')
        return response


# GET /books/isbn
@app.route('/books/<int:isbn>')
def get_book_by_isbn(isbn):
    return_value = {}

    for book in books:
        if book["isbn"] == isbn:
            return_value = {
                'name': book["name"],
                'price': book["price"]
            }
    return jsonify(return_value)


# PUT /books/isbn
@app.route('/books/<int:isbn>', methods=['PUT'])
def replace_book(isbn):
    request_data = request.get_json()
    new_book = {
        'name': request_data['name'],
        'price': request_data['price'],
        'isbn': isbn
    }
    i = 0
    for book in books:
        currentIsbn = book['isbn']
        if currentIsbn == isbn:
            books[i] = new_book
        i += 1
    response = Response("Success", status=202, mimetype='text/plain')
    return response


# PATCH /books/isbn
@app.route('/books/<int:isbn>', methods=['PATCH'])
def update_book(isbn):
    request_data = request.get_json()
    updated_book = {}
    if('name' in request_data):
        updated_book['name'] = request_data['name']
    if('price' in request_data):
        updated_book['price'] = request_data['price']
    for book in books:
        if book['isbn'] == isbn:
            book.update(updated_book)
    response = Response('', status=204)
    response.headers['Location'] = "/books/" + str(isbn)
    return response

app.run(port=5328)
