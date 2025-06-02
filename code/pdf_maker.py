from fpdf import FPDF
import os, sys
from fpdf.enums import XPos, YPos
import re

def resource_path(relative_path):
    """獲取打包後的檔案路徑"""
    if hasattr(sys, '_MEIPASS'):
        # 打包後，檔案位於臨時目錄 sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # 開發環境，使用當前目錄
        base_path = os.path.abspath("..")
    return os.path.join(base_path, relative_path)




# --- PDF Class for Header/Footer ---
class MyPDF(FPDF):
    # These will be set by the StudentReportGenerator's __init__
    def __init__(self, font_name, font_regular_path, font_bold_path, font_italic_path):
        super().__init__()
        self.font_name = font_name
        # 載入字型
        self.add_font(font_name, "", font_regular_path)
        self.add_font(font_name, "B", font_bold_path)
        self.add_font(font_name, "I", font_italic_path)

    def header(self):
        self.set_font(self.font_name, 'B', 20)
        self.cell(0, 10, '學生甄試資料表', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_name, 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)

# --- Main Report Generator Class ---
class StudentReportGenerator:
    def __init__(self, data, font_dir="./font/", image_dir="./images/"):
        self.data = data
        self.font_dir = font_dir
        self.image_dir = image_dir

        self.font_name = "MicrosoftJhengHei" # Use the font name defined in MyPDF
        self.font_regular_path = resource_path(os.path.join("font", "msjh.ttc"))
        self.font_bold_path = resource_path(os.path.join("font", "msjhbd.ttc")) # Corrected variable name from font_blod_path
        self.font_italic_path = resource_path(os.path.join("font", "msjhl.ttc")) # Corrected variable name from font_I_path


        self._check_font_files() # Ensure fonts exist early

        self.pdf = MyPDF(self.font_name, self.font_regular_path, self.font_bold_path, self.font_italic_path)
        self._setup_pdf()

        # --- Table Column Definitions (now class attributes) ---
        self.col_widths = {
            '學測應試號碼': 30, # mm
            '校系名稱': 80,   # mm
            '二階甄試': 20    # mm (This needs to accommodate images)
        }
        self.col_height = 10 # Default cell height for text rows
        self.padding = 5
        # Image dimensions within the table cell
        self.image_cell_width = 10 # mm
        self.image_cell_height = 5 # mm

        self.image_row_padding = 5 # mm
        self.dynamic_image_row_height = self.image_cell_height + self.image_row_padding

        # Calculate total table width for centering
        self.total_table_width = sum(self.col_widths.values())
        self.page_width = self.pdf.w
        self.table_start_x = (self.page_width - self.total_table_width) / 2

    def _check_font_files(self):
        font_files = {
            "regular": self.font_regular_path,
            "bold": self.font_bold_path,
            "italic": self.font_italic_path
        }
        for font_type, path in font_files.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"Error: {font_type} font file '{path}' not found.")

    def _load_fonts(self):
        try:
            self.pdf.add_font(self.font_name, "", self.font_regular_path)
            self.pdf.add_font(self.font_name, "B", self.font_bold_path)
            self.pdf.add_font(self.font_name, "I", self.font_italic_path)
        except UserWarning as UW:
            pass
        
        except Exception as e:
            print(f"字型載入失敗 {e}, 使用預設字型")
            self.pdf.set_font("Arial", "", 9)

    def _setup_pdf(self):
        """Configures the PDF document."""
        
        #self._load_fonts()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
         # Add fonts to the PDF instance
        self.pdf.set_font(self.font_name, size=9) # Set base font size for table content

    def _hex_to_rgb(self, hex_color):
        """Converts hex color string to RGB tuple."""
        if not hex_color or not re.match(r'^#?[0-9A-Fa-f]{6}$', hex_color):
            return (255, 255, 255)
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))\
        
    def _ensure_page_space(self, required_height):
        if self.pdf.get_y() + required_height > (self.pdf.h - self.pdf.b_margin):
            self.pdf.add_page()
            self._draw_table_header()

    def _draw_table_header(self):
        """Draws the table headers."""
        self.pdf.set_font(self.font_name, 'B', size=10)
        self.pdf.set_fill_color(220, 220, 220)

        self.pdf.set_x(self.table_start_x)
        self.pdf.cell(self.col_widths['學測應試號碼'], self.col_height, '學測應試號碼', border=1, align='C', fill=True)
        self.pdf.cell(self.col_widths['校系名稱'], self.col_height, '校系名稱', border=1, align='C', fill=True)
        self.pdf.cell(self.col_widths['二階甄試'], self.col_height, '二階甄試', border=1, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.pdf.set_font(self.font_name, size=9) # Reset font for content
        self.pdf.set_fill_color(255, 255, 255) # Reset fill color

    def _draw_student_record(self, student_record):
        """Draws a single student's data block in the table."""
        num_entries = max(len(student_record['校系名稱']), len(student_record['二階甄試']))
        color_idx = 0

        for i in range(num_entries):
            current_row_height = self.col_height
            exam_detail = student_record['二階甄試'][i] if i < len(student_record['二階甄試']) else ''
            is_image_path = isinstance(exam_detail, str) and (exam_detail.lower().endswith('.png') or exam_detail.lower().endswith('.jpg') or exam_detail.lower().endswith('.jpeg'))
            
            if is_image_path:
                current_row_height = self.dynamic_image_row_height

            # Check for page break BEFORE drawing cells for the current row
            self._ensure_page_space(current_row_height)

            # --- Draw 學測應試號碼 column ---
            self.pdf.set_x(self.table_start_x)
            
            if i == 0:
                self.pdf.set_fill_color(222, 222, 220) # Reset fill color
                self.pdf.cell(self.col_widths['學測應試號碼'], current_row_height, student_record['學測應試號碼'], border=1, align='C', fill=True)
            else:
                self.pdf.cell(self.col_widths['學測應試號碼'], current_row_height, '', border=1) # Draw empty cell for border
            
            current_x = self.pdf.get_x()
            current_y = self.pdf.get_y()

            # --- Draw 校系名稱 ---
            school_dept_name = student_record['校系名稱'][i].replace('\n', ' ').strip() if i < len(student_record['校系名稱']) else ''
            
            # Text color based on data for 校系名稱
            self.pdf.set_text_color(0, 0, 0)
            self.pdf.set_xy(current_x, current_y)
            self.pdf.multi_cell(self.col_widths['校系名稱'], self.col_height, school_dept_name, border=1)

            # --- Draw 二階甄試 with background color ---
            self.pdf.set_xy(current_x + self.col_widths['校系名稱'], current_y)
            
            if color_idx < len(student_record['color']) and is_image_path:
                rgb_bg_color = self._hex_to_rgb(student_record['color'][color_idx])
                self.pdf.set_fill_color(*rgb_bg_color)
                color_idx += 1
            else:
                self.pdf.set_fill_color(255, 255, 255) # Default to white background

            if is_image_path:
                image_full_path = os.path.join(self.image_dir, os.path.basename(exam_detail))
                if os.path.exists(image_full_path):
                    self.pdf.cell(self.col_widths['二階甄試'], current_row_height, '', border=1, align='C', fill=True)
                    
                    img_x = self.pdf.get_x() - self.col_widths['二階甄試']
                    img_y = self.pdf.get_y()
                    
                    center_x_offset = (self.col_widths['二階甄試'] - self.image_cell_width) / 2
                    center_y_offset = (current_row_height - self.image_cell_height) / 2

                    self.pdf.image(image_full_path, 
                                   x=img_x + center_x_offset, 
                                   y=img_y + center_y_offset,
                                   w=self.image_cell_width, 
                                   h=self.image_cell_height)
                    
                    self.pdf.set_y(current_y + current_row_height)
                    self.pdf.set_x(self.table_start_x)
                else:
                    self.pdf.multi_cell(self.col_widths['二階甄試'], self.col_height, f"[Image not found: {os.path.basename(image_full_path)}]", border=1, fill=True)
                    self.pdf.set_y(current_y + current_row_height)
                    self.pdf.set_x(self.table_start_x)
            else:
                self.pdf.multi_cell(self.col_widths['二階甄試'], self.col_height, str(exam_detail), border=1, fill=True)
                self.pdf.set_y(current_y + current_row_height)
                self.pdf.set_x(self.table_start_x)

            self.pdf.set_fill_color(255, 255, 255) # Reset fill color
    
    def generate_pdf(self, output_filename="result.pdf"):
        """Generates the full PDF report."""
        self._draw_table_header()
        for student_record in self.data:
            self._draw_student_record(student_record)
        self.pdf.output(output_filename)
        print(f"✅PDF '{output_filename}' created successfully!")
        

