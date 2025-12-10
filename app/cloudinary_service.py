import cloudinary
import cloudinary.uploader
from flask import current_app


def upload_docx_to_cloudinary(file):
    cloudinary.config(
        cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=current_app.config["CLOUDINARY_API_KEY"],
        api_secret=current_app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )

    upload = cloudinary.uploader.upload(
        file,
        resource_type="raw",
        folder="grader_assignments",
        use_filename=True,
        unique_filename=True,
    )

    return upload["secure_url"]
