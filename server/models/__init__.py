from .user import User
from .recipe import Recipe
from .comment import Comment

# Delayed relationship binding to avoid circular imports
User.recipes = db.relationship('Recipe', backref='author', lazy=True)
User.comments = db.relationship('Comment', backref='author', lazy=True)
