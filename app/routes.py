from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, Response, stream_with_context
from werkzeug.utils import secure_filename
import os
import pdfplumber
from bidi.algorithm import get_display
from docx import Document
import faiss
import json
from sentence_transformers import SentenceTransformer
import logging
import re

from flask import Flask, render_template

app = Flask(__name__)

# כל שאר ההגדרות שלך:
# הגדרת routes ובלוגיקה של האפליקציה

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Railway נותן את PORT דרך משתנה סביבה
    app.run(host="0.0.0.0", port=port, debug=True)


bp = Blueprint('main', __name__)



@bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@bp.route('/search', methods=['GET'])
def search_page():
    return render_template('search.html')

@bp.route('/search', methods=['POST'])
def search_query():
    data = request.get_json()
    query = data.get('query')

    if not query:
        return {"error": "Query is required"}, 400

    results = search_in_embeddings(query)

    # שיפור כל תוצאה לכלול את כל המידע הדרוש
    enhanced_results = [
        {
            "text": result['text'],
            "source": result['source'],  # הוסף את מקור הקובץ
            "division_method": result['division_method']  # שיטת החלוקה
        }
        for result in results
    ]

    return {"results": enhanced_results}, 200




@bp.route('/process', methods=['POST'])
def process_file():
    file = request.files.get('document')
    strategy = request.form.get('strategy')

    if not file or not file.filename:
        return Response("No file selected.<br>", content_type='text/html')

    # בדיקת סוג הקובץ
    filename = secure_filename(file.filename)
    if not check_file_type(filename):
        return Response("Invalid file type. Please upload a valid PDF or DOCX file.<br>", content_type='text/html')

    # שמירת הקובץ בתיקייה
    upload_folder = ensure_upload_folder()
    filepath = os.path.join(upload_folder, filename)
    try:
        file.save(filepath)
        print(f"File saved to {filepath}")
    except Exception as e:
        return Response(f"Error saving file: {e}<br>", content_type='text/html')

    def process_file_stream(filepath, strategy):
        """
        תהליך העיבוד של הקובץ בזמן אמת.
        """
        yield "File uploaded successfully.<br>"

        yield "Extracting text from file...<br>"
        text = extract_text(filepath)
        if not text:
            yield "Failed to extract text. Stopping process.<br>"
            return
        yield "Text extraction completed.<br>"

        yield f"Selected strategy: {strategy}<br>"
        if strategy not in ['fixed', 'sentence', 'paragraph']:
            yield "Invalid processing strategy selected. Stopping process.<br>"
            return

        yield f"Processing text with {strategy} strategy...<br>"
        processed_data = process_text(text, strategy)
        yield f"Processed {len(processed_data)} chunks.<br>"

        yield "Generating embeddings...<br>"
        embeddings = generate_embeddings(processed_data)
        yield "Embeddings generated successfully.<br>"

        yield "Saving data to database...<br>"
        save_to_faiss(processed_data, embeddings, filepath, strategy)  # כאן תוספת של המשתנה strategy
        yield "Processing completed successfully!<br>"

    return Response(stream_with_context(process_file_stream(filepath, strategy)),
                    content_type='text/html')


@bp.route('/status-page', methods=['GET'])
def status_page():
    return render_template('status.html')

@bp.route('/status', methods=['GET'])
def get_status():
    try:
        document_status_file = 'document_status.json'
        
        # בדוק אם הקובץ קיים
        if os.path.exists(document_status_file):
            with open(document_status_file, 'r') as f:
                document_status = json.load(f)

            # מחזיר את תוכן המידע על המסמכים
            return {"documents": document_status}, 200

        return {"documents": []}, 200  # אם הקובץ ריק או לא קיים
    except Exception as e:
        return {"error": f"Error processing status: {str(e)}"}, 500



@bp.route('/reset', methods=['POST'])
def reset_database():
    try:
        # מחיקת קבצי המאגר
        if os.path.exists('faiss_index.bin'):
            os.remove('faiss_index.bin')
        if os.path.exists('faiss_metadata.json'):
            os.remove('faiss_metadata.json')
        if os.path.exists('faiss_texts.txt'):
            os.remove('faiss_texts.txt')
        if os.path.exists('document_status.json'):
            os.remove('document_status.json')

        return {"message": "Database has been reset successfully."}, 200
    except Exception as e:
        return {"error": str(e)}, 500



def check_file_type(filename):
    valid_extensions = ['.pdf', '.docx']
    return any(filename.endswith(ext) for ext in valid_extensions)

def extract_text(file_path):
    """
    מחלץ טקסט מקובץ PDF או DOCX, כולל התאמת כיווניות לטקסט בעברית ושמירה על מבנה פסקאות.
    """
    flash(f'Starting text extraction from {file_path}')
    extracted_text = ""

    try:
        if file_path.endswith('.pdf'):
            with pdfplumber.open(file_path) as pdf:
                pages = []
                for page in pdf.pages:
                    # השתמש בזיהוי רווחים גדולים לקביעת פסקאות
                    page_text = page.extract_text(x_tolerance=3, y_tolerance=10)
                    if page_text:
                        # חלוקה לפסקאות על ידי זיהוי שורות ריקות
                        paragraphs = page_text.split('\n')
                        filtered_paragraphs = [para for para in paragraphs if para.strip()]
                        formatted_text = '\n\n'.join(filtered_paragraphs)
                        pages.append(formatted_text)
                extracted_text = "\n\n".join(pages)

        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
            extracted_text = "\n\n".join(paragraphs)

        else:
            flash('Unsupported file type for text extraction.')
            return None

        # שמירת הטקסט לקובץ טקסט לבדיקה
        extracted_text_file = file_path.replace('.pdf', '.txt').replace('.docx', '.txt')
        with open(extracted_text_file, 'w') as f:
            f.write(extracted_text)
        flash(f'Text extracted and saved to {extracted_text_file}')
        print(f'Text saved to: {extracted_text_file}')

    except Exception as e:
        flash(f'Error extracting text from file: {e}')
        print(f"Error extracting text from file: {e}")

    return extracted_text




def split_fixed(text, chunk_size=100, overlap=20):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - overlap)]


def split_by_sentence(text):
    # שימוש ברג'קס לחלוקה לפי נקודות
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]

def split_by_paragraph(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return [para.strip() for para in text.split('\n\n') if para.strip()]



def process_text(text, strategy):
    split_methods = {
        'fixed': split_fixed,
        'sentence': split_by_sentence,
        'paragraph': split_by_paragraph
    }
    chunks = split_methods.get(strategy, lambda x: [])(text)

    # הוספת לוגים לבדיקה
    print(f"Processed {len(chunks)} chunks using strategy: {strategy}")
    for i, chunk in enumerate(chunks[:5]):  # הצגת 5 פסקאות ראשונות בלבד
        print(f"Chunk {i + 1}: {chunk[:100]}...")  # הדפסת 100 תווים ראשונים מכל פסקה
    return chunks

def save_to_faiss(chunks, embeddings, source_file, strategy):
    try:
        dimension = embeddings.shape[1]
        index_file = 'faiss_index.bin'

        # אם מאגר FAISS קיים, טען אותו
        if os.path.exists(index_file):
            index = faiss.read_index(index_file)
        else:
            index = faiss.IndexFlatL2(dimension)

        # הוספת Embeddings
        index.add(embeddings)
        faiss.write_index(index, index_file)

        # שמירת מטה-דאטה לכל צ'אנק עם הוספת שיטת החלוקה
        metadata_file = 'faiss_metadata.json'
        metadata = []
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

        chunk_metadata = [
            {
                "id": idx,
                "text": chunk,
                "source": source_file,
                "chunk_number": idx + 1,
                "strategy": strategy  # שומר את שיטת החלוקה
            }
            for idx, chunk in enumerate(chunks)
        ]
        metadata.extend(chunk_metadata)

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)

        # שמירת מידע מסכם למסמכים עם שיטת החלוקה
        document_status_file = 'document_status.json'
        document_status = []
        if os.path.exists(document_status_file):
            with open(document_status_file, 'r') as f:
                document_status = json.load(f)

        document_status.append({
            "source": source_file,
            "chunk_count": len(chunks),
            "strategy": strategy  # שומר גם כאן את שיטת החלוקה
        })

        with open(document_status_file, 'w') as f:
            json.dump(document_status, f, indent=4)

        logging.info("Data saved successfully!")
    except Exception as e:
        logging.error(f"Error saving to FAISS: {e}")




# פונקציה עזר ליצירת תיקיות
def ensure_upload_folder():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"Created uploads directory: {upload_folder}")
    return upload_folder


def generate_embeddings(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks)
    return embeddings

def search_in_embeddings(query, k=3):
    """
    מבצע חיפוש במאגר הוקטורי על סמך שאלה
    :param query: השאלה או הטקסט לחיפוש
    :param k: מספר התוצאות הקרובות שצריך להחזיר
    :return: רשימה של מקטעי טקסט תואמים
    """
    try:
        # טוענים את מודל ה-embeddings
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # ממירים את השאלה ל-embedding
        query_embedding = model.encode([query])

        # טוענים את המאגר הוקטורי
        index_file = 'faiss_index.bin'
        index = faiss.read_index(index_file)

        # מבצעים חיפוש של K התוצאות הקרובות ביותר
        distances, indices = index.search(query_embedding, k)

        # טוענים את המטא-דאטה
        metadata_file = 'faiss_metadata.json'
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        # מחזירים את המקטעים הקרובים ביותר
        results = []
        for idx in indices[0]:
            if idx < len(metadata):
                result_data = metadata[idx]
                results.append({
                    "text": result_data.get('text', ''),
                    "source": result_data.get('source', 'Unknown'),  # ודא שהשדה source קיים
                    "division_method": result_data.get('strategy', 'Unknown')  # שם השדה צריך להתאים
                })
            else:
                print(f"Warning: Index {idx} is out of bounds for metadata.")

        return results

    except Exception as e:
        print(f"Error during search: {e}")
        return []
