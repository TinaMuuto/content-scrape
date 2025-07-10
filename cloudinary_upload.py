import os
import cloudinary
import cloudinary.uploader

# DEBUG: Print Cloudinary URL env var
print("DEBUG: CLOUDINARY_URL =", os.environ.get("CLOUDINARY_URL"))

def upload_to_cloudinary(file_path):
    result = cloudinary.uploader.upload(file_path)
    return result["secure_url"]
