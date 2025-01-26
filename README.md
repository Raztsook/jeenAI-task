### README: Text Segmentation, Embedding Creation, and Vector Storage Module

---

## **Overview**
This project is a Python-based module designed to process text documents in various formats (PDF and DOCX), segment them into meaningful chunks using different strategies, generate embeddings for these chunks with modern embedding models, and store the embeddings in a vector database for efficient retrieval.

The project includes an interactive web interface that enables:
1. Uploading documents and selecting a segmentation strategy.
2. Sending queries and retrieving relevant results from the database.
3. Viewing the current status of the database.

---

## **Project Features**

### **1. Text Segmentation (Chunking)**
- **Implementation:**
  - **Fixed-size Overlapping Chunking**: Divides text into chunks of a fixed size with overlapping sections.
  - **Sentence-Based Segmentation**: Splits text based on sentence boundaries.
  - **Paragraph-Based Segmentation**: Splits text based on paragraph boundaries.

- **Technology Used**: 
  - **Python** with regex and custom logic for sentence and paragraph identification.
  - **Alternatives**: Libraries like `NLTK` or `spaCy` can be used for sentence and paragraph splitting.

### **2. Embedding Creation**
- **Implementation**:
  - Generated embeddings using the **SentenceTransformer** library with the `all-MiniLM-L6-v2` model.

- **Advantages**:
  - The model provides efficient and high-quality embeddings for semantic similarity tasks.

- **Alternatives**:
  - Other pre-trained models like OpenAI’s `CLIP`, or language models like `BERT`, can be considered based on accuracy or computational requirements.

### **3. Vector Database for Storage**
- **Implementation**:
  - Used **FAISS** (Facebook AI Similarity Search) for storing and managing vector embeddings locally.

- **Advantages**:
  - FAISS offers highly efficient indexing and searching for vector data, making it ideal for semantic retrieval tasks.

- **Alternatives**:
  - Cloud-based vector databases like **Pinecone**, **Weaviate**, or **Milvus** can be used for larger-scale applications.

### **4. Query Processing**
- **Features**:
  - Queries are converted to embeddings and matched against stored chunks to retrieve the most relevant results.
  - Results include the chunk text, source document, and segmentation strategy used.

---
נכון, הנה הגרסה המעודכנת של החלק ב-README בפורמט אחיד:

```markdown
## **Usage**

### **1. Prerequisites**
Before running the application, follow these steps:

- **Set up a virtual environment** (optional, but recommended):
  ```bash
  python -m venv env39
  ```

- **Activate the virtual environment**:
  - On **Mac/Linux**:
    ```bash
    source env39/bin/activate
    ```
  - On **Windows**:
    ```bash
    .\env39\Scripts\activate
    ```

- **Install the necessary Python packages**:
  ```bash
  pip install -r requirements.txt
  ```

### **2. Running the Application**
To start the Flask application, run the following command:

```bash
flask run
```

Once the server is running, open your browser and go to:

```
http://127.0.0.1:5000/
```

### **3. Functionalities**
- **Upload Documents**: Choose a PDF or DOCX file and select a segmentation strategy to process and store the embeddings.
- **Query the Database**: Enter a query to retrieve semantically relevant chunks from the database.
- **View Database Status**: Check how many documents and chunks are currently stored in the database.
```


---

## **Directory Structure**
```
project/
│
├── app/
│   ├── templates/         # HTML templates for the web interface
│   ├── static/            # Static files (CSS, JavaScript)
│   ├── routes.py          # Main Flask routes
│   ├── utils.py           # Helper functions (e.g., text extraction, segmentation)
│
├── uploads/               # Uploaded documents
├── database/              # Stored vector files and metadata
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
```

---

## **Future Enhancements**
1. **Expand Segmentation Strategies**:
   - Add AI-powered segmentation using fine-tuned models.
2. **Cloud Integration**:
   - Replace local FAISS with scalable solutions like Pinecone or AWS.
3. **Improved Text Processing**:
   - Use advanced NLP libraries for better sentence and paragraph detection.
4. **Support for More File Formats**:
   - Include formats like TXT, CSV, and HTML.

---

## **Conclusion**
This project demonstrates a complete pipeline for processing, embedding, storing, and querying text data. It leverages modern AI tools for efficient semantic search while providing a user-friendly interface. The modular design allows for easy customization and scaling.