# server/seed.py
from server.app import create_app, db
from server.models import User, Recipe, Comment  # Import your Comment model
from werkzeug.security import generate_password_hash
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize the app
app = create_app()

# Initialize Faker
fake = Faker()

def clear_data():
    """Clear existing data"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database cleared and recreated")

def seed_users(num=5):
    """Seed users"""
    with app.app_context():
        # Add a test user with known credentials
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("password123")
        )
        db.session.add(test_user)
        
        # Add fake users
        for _ in range(num - 1):
            user = User(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password_hash=generate_password_hash(fake.password())
            )
            db.session.add(user)
        
        db.session.commit()
        print(f"🌱 Seeded {num} users (including test@example.com/password123)")

def seed_recipes(num=20):
    """Seed recipes"""
    with app.app_context():
        users = User.query.all()
        
        for _ in range(num):
            recipe = Recipe(
                title=fake.sentence(nb_words=3).replace('.', ''),
                ingredients="\n".join([f"- {fake.word().capitalize()} {random.choice(['1 cup', '2 tbsp', '3 cloves', '200g'])}" 
                              for _ in range(5)]),
                instructions="\n".join([f"{i+1}. {fake.sentence()}" 
                                for i in range(5)]),
                prep_time=random.randint(5, 30),
                cook_time=random.randint(10, 60),
                servings=random.randint(1, 8),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                user_id=random.choice(users).id,
                image_url=f"https://picsum.photos/500/300?food={random.randint(1,1000)}"
            )
            db.session.add(recipe)
        
        db.session.commit()
        print(f"🌱 Seeded {num} recipes")

def seed_comments(num=50):
    """Seed comments"""
    with app.app_context():
        users = User.query.all()
        recipes = Recipe.query.all()
        
        for _ in range(num):
            comment = Comment(
                content=fake.paragraph(nb_sentences=2),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                user_id=random.choice(users).id,
                recipe_id=random.choice(recipes).id
            )
            db.session.add(comment)
        
        db.session.commit()
        print(f"🌱 Seeded {num} comments")

def seed_all():
    """Run all seed functions"""
    clear_data()
    seed_users()
    seed_recipes()
    seed_comments()
    print("✅ Database seeding complete!")

if __name__ == '__main__':
    with app.app_context():
        seed_all()