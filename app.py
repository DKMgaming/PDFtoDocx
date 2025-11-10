import streamlit as st
from docx import Document
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO
import os

# --- LƯU Ý QUAN TRỌNG: ---
# KHÔNG CẦN cấu hình đường dẫn cho Tesseract OCR ở đây.
# Trên Streamlit Cloud, nó sẽ được cài đặt vào PATH.
# Dòng sau đây bị loại bỏ: # pytesseract.pytesseract.tesseract_cmd = r'ĐƯỜNG_DẪN_TỚI_TESSERACT_EXE'
# -------------------------

def pdf_scan_to_docx(pdf_file_bytes):
    """
    Sử dụng OCR để chuyển đổi nội dung PDF đã scan thành text, sau đó lưu vào DOCX.
    """
    doc = Document()
    
    try:
        # 1. Chuyển PDF thành các ảnh (PDF to Image)
        # Sẽ cần 'poppler-utils' được cài đặt trên Streamlit Cloud (qua packages.txt)
        images = convert_from_bytes(pdf_file_bytes)
    except Exception as e:
        st.error(f"Lỗi khi chuyển PDF sang ảnh. Đảm bảo file PDF hợp lệ và đã cài đặt 'poppler-utils': {e}")
        return None
    
    st.info(f"Đã trích xuất **{len(images)}** trang từ file PDF. Đang tiến hành OCR...")
    
    progress_bar = st.progress(0)
    
    # 2. Lặp qua từng ảnh và áp dụng OCR
    for i, image in enumerate(images):
        # Sử dụng pytesseract để trích xuất text từ ảnh (OCR)
        # Sử dụng 'vie+eng' để nhận dạng cả Tiếng Việt và Tiếng Anh (cần packages.txt)
        try:
            text = pytesseract.image_to_string(image, lang='vie+eng')
            
            # 3. Thêm text vào file DOCX
            if text and text.strip():
                doc.add_paragraph(text)
                doc.add_page_break() # Thêm ngắt trang giữa các trang PDF
                
        except pytesseract.TesseractNotFoundError:
            st.error("Lỗi: Không tìm thấy Tesseract OCR. Hãy đảm bảo bạn đã thêm 'tesseract-ocr' vào file **packages.txt**.")
            return None
        except Exception as e:
            st.error(f"Lỗi OCR không xác định ở trang {i+1}: {e}")
            
        progress_bar.progress((i + 1) / len(images))
        
    # 4. Lưu DOCX vào bộ nhớ (BytesIO)
    docx_stream = BytesIO()
    doc.save(docx_stream)
    docx_stream.seek(0)
    
    return docx_stream.getvalue()

## --- Giao diện Streamlit ---
def main():
    st.set_page_config(page_title="PDF Scan sang DOCX", layout="centered")
    st.title("📄 PDF Scan sang DOCX Converter (Hỗ trợ OCR)")
    st.markdown("Sử dụng **OCR (Tesseract)** để chuyển đổi text từ file PDF đã scan thành file Word (.docx).")

    uploaded_file = st.file_uploader(
        "Tải lên file PDF đã scan", 
        type=["pdf"],
        help="Chỉ chấp nhận file định dạng PDF."
    )

    if uploaded_file is not None:
        
        # Chạy chuyển đổi
        with st.spinner('Đang tiến hành chuyển đổi (Bước 1: Tách ảnh, Bước 2: OCR Text)...'):
            # Đọc nội dung file dưới dạng bytes
            pdf_bytes = uploaded_file.read()
            
            docx_bytes = pdf_scan_to_docx(pdf_bytes)

        if docx_bytes:
            st.success("✅ Chuyển đổi hoàn tất! Vui lòng tải xuống file Word.")
            
            # Tạo tên file đầu ra
            output_filename = os.path.splitext(uploaded_file.name)[0] + "_OCR_Output.docx"
            
            # Nút Download
            st.download_button(
                label="Tải xuống File DOCX",
                data=docx_bytes,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        # Không cần else vì lỗi đã được xử lý bên trong pdf_scan_to_docx
        
if __name__ == '__main__':
    main()
