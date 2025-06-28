from .base import db
from .user import User
from .recipe import Recipe
from .comment import Comment

# Fully-qualified string paths to avoid resolution issues
User.recipes = db.relationship('Recipe', backref='author', lazy=True)
User.comments = db.relationship('Comment', backref='author', lazy=True)
