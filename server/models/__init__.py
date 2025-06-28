from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .recipe import Recipe
from .comment import Comment
from .user import User

__all__ = ['db', 'User', 'Recipe', 'Comment']
