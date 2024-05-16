from flask import request, jsonify
from init import *
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

book_schema = BookSchema()
books_schema = BookSchema(many=True)
@app.route('/books', methods=['POST'])
@jwt_required()
def add_book():
    current_user = get_jwt()
    if not current_user['is_admin']:
        return jsonify({'message': 'Admin access required'}), 403
    data = request.get_json()
    new_book = Book(
        title=data['title'],
        author=data['author'],
        publication_date=data['publication_date'],
        genre=data['genre'],
        isbn=data['isbn']
    )
    db.session.add(new_book)
    db.session.commit()
    return book_schema.jsonify(new_book)


@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    return book_schema.jsonify(book)

@app.route('/books/<int:id>', methods=['PUT'])
@jwt_required()
def update_book(id):
    current_user = get_jwt()
    if not current_user['is_admin']:
        return jsonify({'message': 'Admin access required'}), 403
    book = Book.query.get(id)
    data = request.get_json()
    book.title = data['title']
    book.author = data['author']
    book.publication_date = data['publication_date']
    book.genre = data['genre']
    book.isbn = data['isbn']
    db.session.commit()
    return book_schema.jsonify(book)

@app.route('/books/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    current_user = get_jwt()
    if not current_user['is_admin']:
        return jsonify({'message': 'Admin access required'}), 403
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    return '', 204


@app.route('/books/search', methods=['GET'])
def search_books():
    query_params = request.args
    query = Book.query
    if 'title' in query_params:
        query = query.filter(Book.title == query_params['title'])
    if 'author' in query_params:
        query = query.filter(Book.author == query_params['author'])
    if 'genre' in query_params:
        query = query.filter(Book.genre == query_params['genre'])
    if 'publication_date' in query_params:
        query = query.filter(Book.publication_date == query_params['publication_date'])
    return books_schema.jsonify(query.all())


@app.route('/books', methods=['GET'])
def get_sorted_books():
    query = Book.query
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    if order == 'desc':
        query = query.order_by(db.desc(getattr(Book, sort_by)))
    else:
        query = query.order_by(getattr(Book, sort_by))
    # page = request.args.get('page', 1, type=int)
    # per_page = request.args.get('per_page', 10, type=int)
    # books = query.paginate(page, per_page, error_out=False)
    books = query.all()
    return books_schema.jsonify(books)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # return f"{data['is_admin']}"
    hashed_password = generate_password_hash(data['password'], method='pbkdf2')
    new_user = User(username=data['username'], password=hashed_password, is_admin=data.get('is_admin', False))
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message="User registered successfully")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'username': user.username}, additional_claims={"is_admin": user.is_admin})
        return jsonify(access_token=access_token)
    else:
        return jsonify(message="Invalid credentials"), 401