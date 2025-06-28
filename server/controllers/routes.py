import os
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from server.models import db, User, Recipe, Comment
from server.auth import register_user, login_user, get_current_user

def init_routes(app):
    # ---------------- Auth Routes ----------------
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Missing JSON in request'}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({'message': 'Username, email, and password are required'}), 400

        return register_user(username, email, password)

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        return login_user(data['username'], data['password'])

    @app.route('/api/profile', methods=['GET'])
    @jwt_required()
    def profile():
        return get_current_user()

    # ---------------- Recipe Routes ----------------
    @app.route('/api/recipes', methods=['GET', 'POST'])
    @jwt_required()
    def recipes():
        if request.method == 'GET':
            recipes = Recipe.query.all()
            return jsonify([r.to_dict() for r in recipes]), 200

        elif request.method == 'POST':
            data = request.get_json()
            ingredients = ",".join(data['ingredients']) if isinstance(data['ingredients'], list) else data['ingredients']
            new_recipe = Recipe(
                title=data['title'],
                ingredients=ingredients,
                instructions=data['instructions'],
                image_url=data.get('image_url', ''),
                user_id=get_jwt_identity()
            )
            db.session.add(new_recipe)
            db.session.commit()
            return jsonify(new_recipe.to_dict()), 201

    @app.route('/api/recipes/<int:recipe_id>', methods=['GET', 'PUT', 'DELETE'])
    @jwt_required()
    def recipe_detail(recipe_id):
        recipe = Recipe.query.get_or_404(recipe_id)

        if request.method == 'GET':
            return jsonify(recipe.to_dict()), 200

        elif request.method == 'PUT':
            if recipe.user_id != get_jwt_identity():
                return jsonify({"message": "Unauthorized"}), 403

            data = request.get_json()
            recipe.title = data.get('title', recipe.title)
            recipe.ingredients = ",".join(data['ingredients']) if isinstance(data['ingredients'], list) else data.get('ingredients', recipe.ingredients)
            recipe.instructions = data.get('instructions', recipe.instructions)
            recipe.image_url = data.get('image_url', recipe.image_url)
            db.session.commit()
            return jsonify(recipe.to_dict()), 200

        elif request.method == 'DELETE':
            if recipe.user_id != get_jwt_identity():
                return jsonify({"message": "Unauthorized"}), 403

            db.session.delete(recipe)
            db.session.commit()
            return jsonify({"message": "Recipe deleted"}), 200

    # ---------------- Comment Routes ----------------
    @app.route('/api/comments/<int:recipe_id>', methods=['POST'])
    @jwt_required()
    def add_comment(recipe_id):
        data = request.get_json()
        new_comment = Comment(
            text=data['text'],
            user_id=get_jwt_identity(),
            recipe_id=recipe_id
        )
        db.session.add(new_comment)
        db.session.commit()
        return jsonify(new_comment.to_dict()), 201

    @app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
    @jwt_required()
    def delete_comment(comment_id):
        comment = Comment.query.get_or_404(comment_id)
        if comment.user_id != get_jwt_identity():
            return jsonify({"message": "Unauthorized"}), 403

        db.session.delete(comment)
        db.session.commit()
        return jsonify({"message": "Comment deleted"}), 200

    # ---------------- Search Route ----------------
    @app.route('/api/search', methods=['GET'])
    def search():
        query = request.args.get('q', '')
        recipes = Recipe.query.filter(Recipe.title.contains(query)).all()
        return jsonify([r.to_dict() for r in recipes]), 200

    # ---------------- User Routes ----------------
    @app.route('/api/users', methods=['GET'])
    @jwt_required()
    def get_users():
        users = User.query.all()
        return jsonify([u.to_dict() for u in users]), 200

    @app.route('/api/users/<int:user_id>', methods=['GET'])
    @jwt_required()
    def get_user(user_id):
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict(include_recipes=True)), 200

    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    @jwt_required()
    def update_user(user_id):
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"message": "Unauthorized"}), 403

        user = User.query.get_or_404(user_id)
        data = request.get_json()

        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])

        db.session.commit()
        return jsonify({"message": "User updated"}), 200

    @app.route('/api/users/<int:user_id>', methods=['DELETE'])
    @jwt_required()
    def delete_user(user_id):
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"message": "Unauthorized"}), 403

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"}), 200

    # ---------------- Upload Image Route ----------------
    @app.route('/api/upload', methods=['POST'])
    @jwt_required()
    def upload_image():
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        filename = secure_filename(file.filename)
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        file_path = os.path.join(uploads_dir, filename)
        file.save(file_path)

        return jsonify({'url': f'/uploads/{filename}'}), 200
