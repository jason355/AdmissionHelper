from seleniumbase import Driver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time, base64, io, re, os, shutil
from PIL import Image as PILImage
import pdf_maker as Pdf
import pytesseract
from itertools import islice
 

def OCR(img_data):
    try:
        text = pytesseract.image_to_string(img_data, lang="eng")
        cleaned_text = re.sub(r'[^\d]', '', text)
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


def clear_directory(directory_path):
    try:
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
            os.makedirs(directory_path)
        else:
            os.makedirs(directory_path, exist_ok=True)
    except PermissionError:
        raise Exception(directory_path, "無法清空資料夾：權限不足")
    except Exception as e:
        raise Exception(directory_path, f"清空資料夾失敗：{str(e)}")

def split_list(lst, chunk_size=60):
    iterator = iter(lst)
    return list(iter(lambda: list(islice(iterator, chunk_size)), []))

def read_exam_id(file_path):
    """Read serial numbers from a text file into a list."""
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            exam_ids_group = [line.strip() for line in file if line.strip()]
            if not exam_ids_group:
                insert_exam_id(file_path)
                return read_exam_id(file_path)
                 
            return split_list(exam_ids_group)
    except FileNotFoundError:
        # print(f"Error: File {file_path} not found, Creating {file_path}")
        insert_exam_id(file_path)
        return read_exam_id(file_path)
        
    except Exception as e:
        print(f"Error reading exam_ids: {e}")
        return None
def insert_exam_id(file_path):    
    with open(file_path, "w", encoding="utf-8") as file:
        temp = input("請輸入准考證號碼(多筆資料請在每筆最後換行)，兩次換行結束輸入>")
        while temp != "":
            try:
                if len(temp) == 8 and temp.isdigit():
                    file.writelines(temp+"\n")
                temp = input("請輸入准考證號碼(多筆資料請在每筆最後換行)，兩次換行結束輸入>")
            except KeyboardInterrupt as KE:
                break

def submit_form_seleniumbase(exam_ids_group, year):
    """Use SeleniumBase with undetectable mode to submit serial number and scrape results."""
    try:
        url = f"https://www.com.tw/cross/uncontinuequery{year}.html"
        driver = Driver(uc=True)
        
        driver.uc_open_with_reconnect(url, reconnect_time=4)
        
        try:
            driver.uc_gui_click_captcha()
            print("CAPTCHA checkbox clicked")
            time.sleep(0.2)
        except:
            print("No CAPTCHA detected or auto-bypassed")
        html_content_list = []
        for exam_ids in exam_ids_group:
            exam_id = "\n".join(exam_ids) + "\n"
            driver.find_element(By.NAME, "testids").send_keys(exam_id)
            driver.find_element(By.XPATH, "//input[@type='submit']").click()
            driver.find_element(By.TAG_NAME, "table")
            time.sleep(0.1)
            html_content_list.append(driver.page_source)
            driver.click('a:contains("回上一頁(學測應試號碼查榜)")')
        return html_content_list
    except Exception as e:
        print(f"Error during navigation or submission: {e}")
        return None
    finally:
        driver.quit()

def parse_table(html_content_group):
    """Parse the table from the response page, focusing on specific rows."""
    try:
        print("Parsing table...")
        data = []

        for html_content in html_content_group:
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find_all('table')
            table = table[2]

            if not table:
                print("Error: No table found")
                return []
            
            # Get all <tr> tags and process from 3rd to penultimate
            #rows = table.find_all('tr') # Third row (index 2) to penultimate
            rows = [tr for tr in table.find_all('tr')[2:-1] if tr.get('bgcolor')]
            
            print(f"numbers of id:{len(rows)}")
            for i, row in enumerate(rows):
                
                # Find nested table in <td colspan="4">
                nested_table = row.find('td', {'colspan': '4'}).find('table') if row.find('td', {'colspan': '4'}) else None
                if not nested_table:
                    print(f"Skipping row without nested table")
                    continue
                # Extract 學測應試號碼
                id_img = row.find('td', {'width': '25%'}).find('img')
                id_img_src = id_img['src']
                if id_img_src.startswith('data:image/png;base64,'):
                    img_data = id_img_src.split(',')[1]
                    # 載入圖片
                    # Decode base64 to image
                    img_bytes = base64.b64decode(img_data)
                    img_data = PILImage.open(io.BytesIO(img_bytes))
                    exam_id = OCR(img_data)
                    if not exam_id:
                        img_data.save(f"./ocr_failed_images/{i}.png", "PNG")
                    else:
                        #img_data.save(f"./ocr_failed_images/{i}.png", "PNG")
                        exam_id = str(exam_id)
                college_name = []
                status = []
                colors = []
                count = 1
                # Process each row in the nested table
                for nested_row in nested_table.find_all('tr'):
                    
                    cols = nested_row.find_all('td')
                    if len(cols) >= 3:
                        # Extract 校系名稱 from <td width="77%">
                        college_td = nested_row.find('td', {'width': '77%'})
                        college_name_now = college_td.find('a').text.strip() + '\n' if college_td and college_td.find('a') else "無資料\n"
                        college_name.append(college_name_now)
                        # Extract 正備取 from <td width="16%">
                        status_td = nested_row.find('td', {'width': '16%'})
                        if status_td:
                            center_div = status_td.find('div', {'align': 'center'})
                            img_src = center_div.find('img')['src'] if center_div and center_div.find('img') else ''
                            div_class = center_div['class'][0] if center_div and center_div.get('class') else ''
                            # Inside parse_table, replace the image-saving block:
                            if img_src.startswith('data:image/png;base64,'):
                                img_data = img_src.split(',')[1]
                                # Decode base64 to image
                                img_bytes = base64.b64decode(img_data)
                                img = PILImage.open(io.BytesIO(img_bytes))
                                # Convert image to RGB if it has transparency
                                # Create new image with background
                                if div_class == "m_leftred":
                                    colors.append("FF0000")
                                    bg_color = (255, 0, 0)  
                                elif div_class == "m_leftgreen":
                                    colors.append("168716")
                                    bg_color = (0, 255, 0)
                                bg_image = PILImage.new('RGBA', img.size, bg_color)
                                bg_image.paste(img, (0, 0))
                                
                                # Save image
                                img_filename = f"./images/{exam_id}_{count}.png"
                                count += 1
                                bg_image.save(img_filename, 'PNG')
                                img_src = img_filename
                                
                            status_now =  img_src   if img_src else (status_td.find('div', class_='m_retestdate').text.strip() if status_td.find('div', class_='m_retestdate').text.strip() else '未知')
                            status.append(status_now)
                    else:
                        print(f"Skipping nested row with insufficient columns: {cols}")
                # Use submitted serial number for 學測應試號碼
                data.append({
                    '學測應試號碼': exam_id,
                    '校系名稱': college_name,
                    '二階甄試': status,
                    'color':colors
                })

        
        #print(f"Parsed data: {data}")
        return data
    except Exception as e:
        print(f"Error parsing table: {e}")
        return []



def save_to_pdf(data, year, output_file='results.pdf'):
    print(f"saveing to {output_file}...")

    # Instantiate the generator and create the PDF
    generator = Pdf.StudentReportGenerator(data, year)
    generator.generate_pdf(output_file)


