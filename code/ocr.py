import pytesseract
from PIL import Image
import re
import base64, io


def OCR_(image_path):
    try:
        # 載入圖片
        # 初始化 List 用於儲存八位數字
        eight_digit_list = []
        image = Image.open(image_path)
        
        # 使用 pytesseract 提取文字
        text = pytesseract.image_to_string(image, lang="eng")
        print(text)
        cleaned_text = re.sub(r'[^\d]', '', text)
        print(cleaned_text)
        pattern = r'^\d{8}$'
        if text == None or len(text) == 0:
            return False
        match = re.match(pattern, cleaned_text)
        if match:
            return match.group(0)
        else:
            return False

    except FileNotFoundError:
        print(f"圖片檔案 {image_path} 不存在")
    except Exception as e:
        print(f"OCR 處理時發生錯誤: {e}")

        
def OCR(img_data):
    try:
        # 載入圖片
        # Decode base64 to image
        img_data = img_data.split(',')[1]
        print(img_data)
        img_bytes = base64.b64decode(img_data)
        image = Image.open(io.BytesIO(img_bytes))

        text = pytesseract.image_to_string(image, lang="eng")
        print(text)
        cleaned_text = re.sub(r'[^\d]', '', text)
        print(cleaned_text)
        pattern = r'^\d{8}$'
        if text == None or len(text) == 0:
            return False
        match = re.match(pattern, cleaned_text)
        if match:
            return match.group(0)
        else:
            return False

    except FileNotFoundError:
        print(f"圖片檔案不存在")
    except Exception as e:
        print(f"OCR 處理時發生錯誤: {e}")

result = OCR_("./ocr_failed_images/35.png")
print(result)