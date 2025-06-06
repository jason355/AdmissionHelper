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
        student_file_path = input("請輸入學生逗號分隔檔(.csv)路徑>") 
        try:
            std_df = Md.read_exam_csv(student_file_path)
        except FileNotFoundError:
            print(f"❌查無此檔案:{student_file_path}")
            main()
        else:
            if std_df.empty:
                return
            std_df["應試號碼"] = std_df["應試號碼"].astype(str)
            exam_ids_group = Md.split_list(std_df["應試號碼"].tolist())
            print(exam_ids_group)
            html_content = Md.submit_form_seleniumbase(exam_ids_group, year)
            if not html_content:
                return
            
            table_data = Md.parse_table(html_content, std_df)
            Md.save_to_pdf(table_data, year)

    
if __name__ == '__main__':
    main()
    input("按下enter結束程式>")