from flask_sqlalchemy import SQLAlchemy
from server.models.base import db

db = SQLAlchemy()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "user": self.author.username,  # from relationship
            "recipe_id": self.recipe_id,
        }
