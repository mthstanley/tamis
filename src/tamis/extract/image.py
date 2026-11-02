import cv2
import pytesseract
from imutils import rotate_bound
from tamis.extract import Extractor
import os
from urllib.parse import urlparse


class ImageExtractor(Extractor):
    def can_extract(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme is not None or parsed.scheme != "file":
            return False
        if not os.path.exists(url):
            return False
        return cv2.imread(url) is not None

    def extract(self, url: str) -> str:
        image = cv2.imread(url, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return ""

        # Upscale by 2x or 3x so the small fraction digits are large enough to be recognized
        resized = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Apply Otsu's thresholding to turn it into crisp black and white
        thresh = cv2.threshold(
            resized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

        # Invert if necessary (Tesseract prefers black text on a white background)
        thresh = cv2.bitwise_not(thresh)

        # Get orientation data dictionary
        osd_data = pytesseract.image_to_osd(thresh, output_type=pytesseract.Output.DICT)
        rotation_angle = osd_data["rotate"]

        processed_image = thresh
        # Correct rotation if needed
        if rotation_angle != 0:
            processed_image = rotate_bound(processed_image, rotation_angle)

        text = pytesseract.image_to_string(processed_image, config="-l eng+equ")
        return text
