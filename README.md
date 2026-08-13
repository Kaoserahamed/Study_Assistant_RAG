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

* Python 3.11 or higher
* Node.js 18+ with npm
* Pinecone API key
* Google Gemini API key

### Setup

**1. Clone the project**

```bash
cd StudentAssistant
```

**2. Setup the backend**

Go to the backend directory:

```bash
cd backend
```

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/student_assistant
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=student-assistant
GEMINI_API_KEY=your_gemini_key
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
python main.py
```

The backend will run on:

```text
http://localhost:8000
```

**3. Setup the frontend**

Open a new terminal and go to the frontend directory:

```bash
cd frontend
```

Create a `.env` file:

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

1. **Create an account** using your email and password.
2. **Upload course materials** such as PDFs, documents, and slides.
3. **Process documents** by extracting text, splitting it into chunks, and creating embeddings.
4. **Ask questions** through the chat interface.
5. **Retrieve relevant content** from Pinecone using semantic search.
6. **Generate answers** using Gemini based on the retrieved content.
7. **Check the sources** and page numbers from the sidebar to verify the answer.

## Notes

* The first upload of a document may take some time because the system needs to process the document and create embeddings.


