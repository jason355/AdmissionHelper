import method as Md
import os
def main():
    Md.clear_directory('./images/')
    Md.clear_directory("./ocr_failed_images")

    year = input("請輸入查詢年分(民國)>")

    if not year.isdigit():
        print("請輸入阿拉伯數字與正確年分")
        main()
    else:
        exam_id_file  = 'exam_ids.txt'

        exam_ids = Md.read_exam_id(exam_id_file)
        if not exam_ids:
            return
        html_content = Md.submit_form_seleniumbase(exam_ids, year)
        if not html_content:
            return
        
        table_data = Md.parse_table(html_content)
        Md.save_to_pdf(table_data, year)

    
if __name__ == '__main__':
    main()
    input("按下enter結束程式>")