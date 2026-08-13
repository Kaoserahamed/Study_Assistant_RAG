# Student Assistant

An AI-powered study assistant that helps students learn from their own course materials. Students can upload PDFs, documents, and slides, then ask questions and get answers based on the uploaded materials.

## Features

* **Smart Document Upload** – Upload PDF, DOCX, PPTX, and TXT files. The system automatically extracts, processes, and chunks the documents for efficient searching.
* **Intelligent Search** – Uses semantic search to find the most relevant sections from uploaded documents based on the user's question.
* **AI-Powered Answers** – Uses Google's Gemini API to generate answers based on the retrieved course materials.
* **Source Citations** – Each answer includes source citations with page numbers so students can verify the information.
* **Document Viewer** – Built-in PDF and text viewer allows students to read their materials while using the chat.
* **Conversation History** – Conversations are saved in the database, so users can refresh the page and continue their previous conversations.

## Technology Stack

### Backend

* **Python 3.11** with FastAPI for building REST APIs
* **SQLAlchemy** for database ORM and data models
* **Pinecone** for vector storage and semantic search
* **Google Gemini API** for generating AI responses
* **PyPDF** for extracting text from PDF files

### Frontend

* **React 18** with TypeScript for building the user interface
* **Vite** as the frontend build tool
* **Tailwind CSS** for styling
* **React Router** for navigation and conversation URLs
* **PDF.js** for displaying PDF files in the browser

### Infrastructure

* Separate frontend and backend architecture
* RESTful API communication
* JWT-based authentication
* Environment-based configuration

## Getting Started

### Prerequisites

Make sure you have the following installed:

* **Python 3.11** or higher
* **Node.js 18+** with npm
* **MySQL 8.0+** database server
* **Pinecone API key** - [Get from Pinecone](https://app.pinecone.io)
* **Google Gemini API key** - [Get from Google AI Studio](https://aistudio.google.com/apikey)

### Quick Setup

**⚠️ Important**: If you're continuing from a previous installation where API keys were exposed, follow `QUICK_START_SECURITY.md` first to rotate your keys.

### Step-by-Step Setup

**1. Clone the project**

```bash
git clone <repository-url>
cd StudentAssistant
```

**2. Setup the database**

Create a MySQL database:

```bash
mysql -u root -p
CREATE DATABASE study_assistant;
EXIT;
```

Run the database schema:

```bash
mysql -u root -p study_assistant < backend/database_schema.sql
```

**3. Setup the backend**

Go to the backend directory:

```bash
cd backend
```

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` file with your actual values:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=study_assistant
DB_PORT=3306

# JWT Configuration - Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your_generated_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=student-assistant
EMBEDDING_DIMENSION=768

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-3.5-flash

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# CORS Configuration (add production domains here)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# RAG Configuration
RAG_MAX_CONTEXT_CHARS=24000
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create Pinecone index (first time only):

```bash
python migrate_pinecone_index.py
```

Start the backend:

```bash
python -m uvicorn main:app --reload
```

The backend will run on:

```text
http://localhost:8000
```

**4. Setup the frontend**

Open a new terminal and go to the frontend directory:

```bash
cd frontend
```

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Install the dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will run on:

```text
http://localhost:5173
```


## How It Works

### RAG (Retrieval-Augmented Generation) Pipeline

1. **Create an account** using your email and password
2. **Upload course materials** (PDF or TXT files, max 50MB)
3. **Document Processing**:
   - Text extraction from PDFs (1400 chars per chunk, 200 overlap)
   - Real embedding generation using Google Gemini text-embedding-004 (768 dimensions)
   - Storage in Pinecone vector database for semantic search
4. **Ask questions** through the chat interface
5. **Semantic search** retrieves top 10 most relevant chunks using cosine similarity
6. **Context building** formats retrieved chunks with citations
7. **AI generation** uses Gemini 3.5-flash to generate answers from context
8. **Source citations** displayed with page numbers and snippets

### Security Features

✅ **Rate Limiting**: Prevents abuse and DoS attacks
- Login: 10 requests/minute
- Registration: 5 requests/hour
- Upload: 10 requests/hour
- Chat: 30 requests/minute

✅ **File Validation**: Type and size checking for uploads

✅ **CORS Protection**: Whitelist-based origin control

✅ **JWT Authentication**: Secure token-based auth with configurable expiration

✅ **Environment-based Secrets**: All API keys in `.env` files

## Useful Commands

### Database Management

```bash
# Clear all documents and chunks
python clear_documents.py

# Recreate entire database
python recreate_database.py

# Migrate Pinecone index
python migrate_pinecone_index.py
```

### Testing

```bash
# Test RAG pipeline
python test_rag_pipeline.py

# Check Pinecone data
python test_pinecone_data.py
```

## Troubleshooting

### Rate Limit Errors (429)
- Wait for the rate limit window to reset
- Limits are per IP address
- See `SECURITY_FIXES_COMPLETE.md` for current limits

### Upload Fails
- Check file type (only PDF and TXT allowed)
- Check file size (max 50MB)
- Check backend logs for detailed error messages

### Empty Search Results
- Make sure documents are fully processed (check backend logs)
- Verify Pinecone index exists: dimension should be 768
- Check if documents belong to your user account

### Database Issues
- Run `python recreate_database.py` to reset
- Or manually: `mysql -u root -p study_assistant < database_schema.sql`

## Documentation

- `README.md` (this file) - Overview and setup
- `QUICK_START_SECURITY.md` - Security setup in 10 minutes
- `SECURITY_FIXES_COMPLETE.md` - All security improvements
- `CRITICAL_ISSUES_AUDIT.md` - Full security audit with 17 issues
- `RAG_PIPELINE_FIXES_COMPLETE.md` - Embedding system details
- `.env.example` - Environment variable template

## Project Structure

```
StudentAssistant/
├── backend/
│   ├── app/
│   │   ├── controllers/      # Request handlers
│   │   ├── models/           # Database models
│   │   ├── repositories/     # Data access layer
│   │   ├── routers/          # API routes with rate limiting
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic (RAG, embeddings, LLM)
│   ├── uploaded_files/       # Uploaded PDFs (gitignored)
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Secrets (NEVER commit!)
│   └── .env.example         # Template for .env
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   └── App.tsx          # Main app component
│   ├── .env                 # Frontend config
│   └── .env.example         # Template
└── README.md
```

## Notes

* The first upload of a document may take some time because the system needs to process the document and create embeddings.




## Notes

* The first upload of a document may take some time because the system needs to process the document and generate real embeddings using the Gemini API.
* All embeddings are generated using Google's text-embedding-004 model (768 dimensions) for high-quality semantic search.
* Rate limits are in place to prevent abuse - see `SECURITY_FIXES_COMPLETE.md` for details.
* For production deployment, see `DEPLOYMENT_GUIDE.md` and rotate all API keys first.

## Contributing

When contributing, please:
1. Never commit `.env` files or API keys
2. Follow the existing code structure
3. Test security features before submitting
4. Update documentation for any changes

## License

[Your License Here]

## Support

For issues, questions, or security concerns, please check:
- `CRITICAL_ISSUES_AUDIT.md` for known security issues
- `SECURITY_FIXES_COMPLETE.md` for security documentation
- Backend logs for debugging information

---

**Version**: 2.0 (Security Hardened)  
**Last Updated**: August 13, 2026
