import io

import cv2
import numpy as np
from PIL import Image


def preprocess_image_rgb_and_grayscale(image_bytes):

    image_np = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_UNCHANGED)

    ## If the image is RGB if the length of shape is more than 2 means its color image
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = Image.open(io.BytesIO(image_bytes))

        image_np = np.array(image)

        ## Detects the lighter and darker red
        hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        mask = mask1 + mask2
        image_np[mask > 0] = [255, 255,
                              255]

        gray = cv2.cvtColor(image_np,
                            cv2.COLOR_RGB2GRAY)

        blurred = cv2.GaussianBlur(gray, (1, 1),
                                   0)

        _, binary = cv2.threshold(blurred, 0, 255,
                                  cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = np.ones((2, 2), np.uint8)
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel,
                                  iterations=1)

        # Step 6: Dilate to make characters more readable
        dilated = cv2.dilate(closed, np.ones((1, 1), np.uint8),
                             iterations=1)

        return dilated
    processed_img = cv2.imdecode(image_np, cv2.IMREAD_GRAYSCALE)
    return processed_img
