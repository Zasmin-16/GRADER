import os

class Config:
    SECRET_KEY = "**************"
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = "**********"
    CLOUDINARY_API_KEY = "**********"
    CLOUDINARY_API_SECRET = "**********"

    # Supabase
    SUPABASE_URL = "**********"
    SUPABASE_KEY = "**********"

    # open AI
    OPENAI_API_KEY = "**************"
