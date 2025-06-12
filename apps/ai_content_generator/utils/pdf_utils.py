import PyPDF2

def extract_text_from_pdf(pdf_file):
    """
    Extrae texto de un archivo PDF.
    
    Args:
        pdf_file: Archivo PDF subido (object de tipo UploadedFile)
        
    Returns:
        str: Texto extraído del PDF
    """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text 