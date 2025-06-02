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
        # 按行分割文字
        line = text.split("\n")
        if len(line) > 1:
            return False
        
        if re.match(r'^\d{8}$', line):
            return line

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
        # 按行分割文字
        if text == None:
            return False
        if re.match(r'^\d{8}$', text):
            return text

    except FileNotFoundError:
        print(f"圖片檔案不存在")
    except Exception as e:
        print(f"OCR 處理時發生錯誤: {e}")

result = OCR("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFoAAAAUCAIAAACCmL1JAAAABnRSTlMA/wD/AP83WBt9AAAACXBIWXMAAA7EAAAOxAGVKw4bAAAA9klEQVRYhe2X0Q7DIAhFZdn//zJ7MDMggoBN2jSct1mu4B1VC4jYij+fuwt4FmUHo+xglB2MsoPx1R4AQGtNnjt9vKM9vURFJaFc/gDJujumUmSCnmMKO1TRcSrxqzzF2Czs2K6q/5yqPFHJNY+RkGq7hC0LO6ZSnGgqYzbbKS1yq0q8I4PAVupsB5torQAQkpx40aIny3AEABIpE7Uab8Ql80+oJ4tGOtlJrYjo/w/kputPGuuO9Ba19ELbIO2pDBVyaLyT8DUsWr0dSd8+GjNGljNoqnMWjSRbgMZoFypNpTWU1D7hGpbZEV9MfbMwyg5G2cH4AcjO9iHfWpmgAAAAAElFTkSuQmCC")
print(result)