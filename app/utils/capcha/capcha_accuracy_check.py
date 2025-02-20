import requests
import easyocr
import os
from PIL import Image

from app.utils.capcha.capcha import preprocess_image_rgb_and_grayscale

reader = easyocr.Reader(['en'])


os.makedirs("captchas", exist_ok=True)

def fetch_captcha():
    url = "https://member.bseindia.com/Handler.ashx"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    return None


def test_captcha_accuracy(n=100):
    correct = 0
    total = 0

    for i in range(n):
        print(f"Processing image {i+1}/{n}...")

        image_bytes = fetch_captcha()
        if not image_bytes:
            print("Failed to fetch image")
            continue

        with open(f"captchas/captcha_original_{i+1}.png", "wb") as f:
            f.write(image_bytes)

        processed_img = preprocess_image_rgb_and_grayscale(image_bytes)

        Image.fromarray(processed_img).save(f"captchas/captcha_processed_{i+1}.png")

        result = reader.readtext(processed_img, detail=0, adjust_contrast=0.7)

        with open(f"captchas/captcha_{i+1}.txt", "w") as f:
            f.write("".join(result))

        if result:
            correct += 1
        total += 1

    accuracy = (correct / total) * 100 if total > 0 else 0
    print(f"OCR Accuracy: {accuracy:.2f}% ({correct}/{total})")

test_captcha_accuracy()
