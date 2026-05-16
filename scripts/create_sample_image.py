from PIL import Image, ImageDraw, ImageFont
import os

def create_sample():
    # Attempt to create a standard 800x400 image for OCR testing
    img = Image.new('RGB', (800, 400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    text = """
My Awesome Video 1
https://youtube.com/watch?v=123456

Another Great Video
https://youtube.com/watch?v=abcdef
"""
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
        
    d.text((20, 20), text, fill=(0, 0, 0), font=font)
    img_path = os.path.join(os.path.dirname(__file__), 'sample_ocr_test.png')
    img.save(img_path)
    print(f"Sample testing image created at: {img_path}")

if __name__ == "__main__":
    create_sample()
