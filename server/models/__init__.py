from .base import db
from .user import User
from .recipe import Recipe
from .comment import Comment

# Set relationships AFTER imports
User.recipes = db.relationship('Recipe', backref='author', lazy=True)
User.comments = db.relationship('Comment', backref='author', lazy=True)
Recipe.comments = db.relationship('Comment', backref='recipe', lazy=True)
