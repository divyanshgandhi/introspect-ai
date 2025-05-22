# Introspect AI

A tool that transforms content from files/links into personalized ChatGPT prompts using a two-hop design.

## Architecture

Introspect AI uses a two-hop design:
1. Extract: Strip every type of input (video, PDF, tweet, image) down to its most usable, action-oriented ideas
2. Personalize: Fuse the extracted insights with user context to generate a personalized ChatGPT prompt

## Setup Instructions

### Prerequisites

- Python 3.8+ with pip
- Node.js 16+ with npm
- Docker and docker-compose (optional, for containerized setup)

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
GOOGLE_API_KEY=your_google_api_key  # Required for Gemini API
```

### Development Setup

#### Option 1: Using the development script

1. Make the script executable:
   ```bash
   chmod +x dev.sh
   ```

2. Run the development script:
   ```bash
   ./dev.sh
   ```

This will:
- Set up Python virtual environment for the backend
- Install backend dependencies
- Start the FastAPI backend server on port 8000
- Install frontend dependencies
- Start the Vite dev server on port 5173

#### Option 2: Manual setup

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000 npm run dev
```

#### Option 3: Using Docker

Build and start the containers:

```bash
docker-compose up --build
```

## Usage

1. Open your browser and navigate to http://localhost:5173
2. Upload a file or enter a YouTube URL
3. Fill in your personal context (interests, goals, background)
4. Click "Generate Personalized Prompt"
5. Copy the generated prompt and paste it into ChatGPT

## API Endpoints

### Extract API
```
POST /api/extract
Content-Type: multipart/form-data
```

### Personalize API
```
POST /api/personalize
Content-Type: application/json
```

### Process API
```
POST /api/process
Content-Type: multipart/form-data
```

## Project Structure

```
introspect-ai/
├── backend/
│   ├── agents/           # Agent implementation using Agno
│   ├── api/              # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Backend container configuration
├── frontend/
│   ├── src/              # React application source
│   ├── package.json      # Node.js dependencies
│   └── Dockerfile        # Frontend container configuration
├── docker-compose.yml    # Docker Compose configuration
└── dev.sh                # Development setup script
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 