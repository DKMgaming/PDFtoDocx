import streamlit as st
from docx import Document
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO
import os

# --- KHẮC PHỤC LỖI STREAMLIT CLOUD (RẤT QUAN TRỌNG) ---
# Chỉ định rõ đường dẫn Tesseract. Trên môi trường Linux/Streamlit Cloud, 
# Tesseract được cài đặt tại đây nhờ vào file packages.txt.
# --- BẢO ĐẢM DÒNG NÀY ĐÃ CÓ VÀ KHÔNG BỊ COMMENT ---
try:
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
except Exception as e:
    st.warning(f"Không thể cấu hình đường dẫn Tesseract: {e}. Có thể Tesseract không được cài đặt hoặc đã nằm trong PATH.")
# ----------------------------------------------------

def pdf_scan_to_docx(pdf_file_bytes):
    """
    Sử dụng OCR để chuyển đổi nội dung PDF đã scan thành text, sau đó lưu vào DOCX.
    """
    doc = Document()
    
    try:
        # Chuyển PDF thành các ảnh (Cần 'poppler-utils' từ packages.txt)
        images = convert_from_bytes(pdf_file_bytes)
    except Exception as e:
        st.error(f"Lỗi khi chuyển PDF sang ảnh. Đảm bảo file PDF hợp lệ và đã cài đặt 'poppler-utils': {e}")
        return None
    
    st.info(f"Đã trích xuất **{len(images)}** trang từ file PDF. Đang tiến hành OCR...")
    
    progress_bar = st.progress(0)
    
    # Lặp qua từng ảnh và áp dụng OCR
    for i, image in enumerate(images):
        try:
            # Sử dụng 'vie+eng' (Cần tesseract-ocr-vie và tesseract-ocr-eng từ packages.txt)
            text = pytesseract.image_to_string(image, lang='vie+eng')
            
            # Thêm text vào file DOCX
            if text and text.strip():
                doc.add_paragraph(text)
                doc.add_page_break()
                
        except pytesseract.TesseractNotFoundError:
            st.error("Lỗi: Không tìm thấy Tesseract OCR. Hãy kiểm tra file **packages.txt**.")
            return None
        except Exception as e:
            st.error(f"Lỗi OCR không xác định ở trang {i+1}: {e}")
            
        progress_bar.progress((i + 1) / len(images))
        
    # Lưu DOCX vào bộ nhớ (BytesIO)
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

if __name__ == '__main__':
    main()
