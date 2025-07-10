import cloudinary
import cloudinary.uploader

def upload_to_cloudinary(file_path):
    result = cloudinary.uploader.upload(file_path)
    return result["secure_url"]
