# Introspect AI

A tool that transforms content from files/links into personalized ChatGPT prompts using a two-hop design.

## Architecture

Introspect AI uses a two-hop design:
1. Extract: Strip every type of input (video, PDF, tweet, image) down to its most usable, action-oriented ideas
2. Personalize: Fuse the extracted insights with user context to generate a personalized ChatGPT prompt

### Microservice Architecture

This application is designed to run as a **microservice** behind your main website's nginx configuration:

```
Main Website (www.divyanshgandhi.com)
├── nginx handles SSL & routing
├── /introspect → Introspect AI Frontend (port 3000)
└── /introspect/api → Introspect AI Backend (port 8000)
```

## Setup Instructions

### Prerequisites

- Python 3.8+ with pip
- Node.js 16+ with npm
- Docker and docker-compose (optional, for containerized setup)

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
GOOGLE_API_KEY=your_google_api_key  # Required for Gemini API
GEMINI_API_KEY=your_gemini_api_key  # Required for Gemini API
EXTRACT_MODEL=gemini-1.5-flash     # Optional, defaults to gemini-1.5-flash
PROMPT_MODEL=gemini-1.5-flash      # Optional, defaults to gemini-1.5-flash
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

#### Option 3: Using Docker (Development)

Build and start the containers:

```bash
docker-compose up --build
```

## 🚀 Production Deployment (Microservice Mode)

This application is designed to run as a microservice behind your main website's nginx configuration.

### Quick Start (Local Testing)

Test the production configuration locally:

```bash
# Copy environment template and edit with your API keys
cp environment.example .env
nano .env

# Test production setup locally
./test-local.sh
```

Visit `http://localhost:3000` to test the frontend directly.

### Production Deployment

1. **Deploy the microservices**:
   ```bash
   # On your server
   git clone <your-repo-url> introspect-ai
   cd introspect-ai
   cp environment.example .env
   nano .env  # Add your API keys
   ./deploy.sh
   ```

2. **Configure your main website nginx** (see [change-request.md](./change-request.md) for details)

3. **Access your app** at: `https://www.divyanshgandhi.com/introspect`

### Services Exposed

- **Frontend**: `localhost:3000` (React SPA with nginx)
- **Backend**: `localhost:8000` (FastAPI)

### Production Features

- ✅ **Containerized microservices** (frontend + backend)
- ✅ **Subdomain routing** via main website nginx
- ✅ **Production-optimized builds** (static frontend, containerized backend)
- ✅ **SSL/HTTPS support** (handled by main website)
- ✅ **Health monitoring** endpoints
- ✅ **Automated deployment** scripts

## Usage

1. Open your browser and navigate to:
   - Development: http://localhost:5173
   - Production: https://www.divyanshgandhi.com/introspect
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

### Rate Limit Status API
```
GET /api/rate-limit-status
```

### Health Check
```
GET /api/health
GET /health
```

## Rate Limiting

The API implements rate limiting to prevent abuse and ensure fair usage:

### Configuration
- **Limit**: 5 requests per 24 hours per IP address
- **Window**: 24-hour sliding window
- **Scope**: All processing endpoints (`/api/extract`, `/api/personalize`, `/api/process`)
- **Identification**: Based on client IP address (supports proxy headers)

### Rate Limit Headers

All API responses include rate limiting headers:

```
X-RateLimit-Limit: 5          # Maximum requests allowed
X-RateLimit-Remaining: 3       # Requests remaining in current window
X-RateLimit-Reset: 1640995200  # Unix timestamp when limit resets
```

### Rate Limit Status Endpoint

Check your current rate limit status:

```bash
curl http://localhost:8000/api/rate-limit-status
```

Response:
```json
{
  "max_requests": 5,
  "window_hours": 24,
  "remaining_requests": 3,
  "reset_time": "2024-01-01T12:00:00",
  "is_limited": false
}
```

### Rate Limit Exceeded Response

When the rate limit is exceeded, the API returns a 429 status code:

```json
{
  "detail": {
    "error": "Rate limit exceeded",
    "message": "Maximum 5 requests allowed per 24 hours",
    "remaining_requests": 0,
    "reset_time": "2024-01-01T12:00:00"
  }
}
```

### Testing Rate Limiting

Use the provided test script to verify rate limiting functionality:

```bash
# Test rate limiting
./scripts/test_rate_limiting.sh
```

## Frontend Rate Limiting Integration

The frontend includes built-in rate limiting support with user-friendly messaging:

### Features
- **Real-time Status**: Displays remaining requests under the generate button
- **Automatic Updates**: Rate limit status refreshes after each API call
- **Error Handling**: Graceful handling of 429 rate limit errors
- **Contact Information**: Direct link to @divyanshgandhi when limits are exceeded

### User Experience
- Users see "X of 5 free requests remaining" below the generate button
- When rate limited, users see a message to contact @divyanshgandhi with a direct X link
- Button is automatically disabled when no requests remain
- Clear error messages distinguish between rate limits and other errors

### Implementation
- `frontend/src/hooks/useRateLimit.ts` - Custom hook for rate limit management
- `frontend/src/components/RateLimitDisplay.tsx` - Rate limit status display
- `frontend/src/lib/api.ts` - Enhanced API client with rate limit support
- `frontend/src/components/ContentExtractor.tsx` - Updated with rate limiting

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
│   └── Dockerfile.prod   # Production frontend container
├── docs/
│   ├── change-request.md     # Main website integration guide
│   ├── README.md            # This file
│   ├── DEPLOYMENT.md        # Deployment instructions
│   ├── prd.md              # Product Requirements Document
│   ├── ed.md               # Engineering Design Document
│   └── *.md                # Other documentation
├── scripts/
│   ├── test-local.sh         # Local testing script
│   └── run_test.sh          # Backend testing script
├── docker-compose.yml    # Development Docker Compose
├── docker-compose.prod.yml # Production Docker Compose (microservice mode)
├── deploy.sh             # Production deployment script
├── dev.sh                # Development setup script
└── start.sh              # Container startup script
```

## Integration with Main Website

See [change-request.md](./change-request.md) for detailed instructions on integrating this microservice with your main website's nginx configuration.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 