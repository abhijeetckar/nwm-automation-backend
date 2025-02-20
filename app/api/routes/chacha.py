from fastapi import APIRouter,UploadFile,File
from PIL import Image,ImageDraw,ImageFont
from app.utils.capcha.capcha import preprocess_image_rgb_and_grayscale
import easyocr
from app.utils.response_handler.response_handler import APIResponse

from fastapi.requests import Request

capcha_router = APIRouter()



@capcha_router.post("/solve_image_captcha")
async def solve_image_captcha(request:Request,file: UploadFile = File(...)):
    reader = easyocr.Reader(['en'], gpu=False)
    image_bytes = await file.read()
    processed_img = preprocess_image_rgb_and_grayscale(image_bytes)
    result = reader.readtext(processed_img, detail=0, adjust_contrast=0.7)
    api_response_obj = APIResponse(request.headers.get("requestId"), status_code="success_response", data={"captcha_text": "".join(result)})
    return await api_response_obj.response_model()