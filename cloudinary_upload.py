import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()  # Læser .env-filen (CLOUDINARY_URL)

def upload_to_cloudinary(file_path):
    result = cloudinary.uploader.upload(file_path)
    return result["secure_url"]
