# Introspect AI

A tool that transforms content from files/links into personalized ChatGPT prompts using a two-hop design.

## Quick Start

### Development
```bash
./dev.sh
```

### Production Testing
```bash
./scripts/test-local.sh
```

### Production Deployment
```bash
./deploy.sh
```

### Test Rate Limiting
```bash
./scripts/test_frontend_rate_limiting.sh
```

## Architecture

Introspect AI uses a two-hop design:
1. **Extract**: Strip every type of input (video, PDF, tweet, image) down to its most usable, action-oriented ideas
2. **Personalize**: Fuse the extracted insights with user context to generate a personalized ChatGPT prompt

### Rate Limiting

The API includes basic rate limiting to prevent abuse:
- **Limit**: 5 requests per 24 hours per IP address
- **Scope**: Applies to all processing endpoints (`/api/extract`, `/api/personalize`, `/api/process`)
- **Headers**: Rate limit information included in response headers
- **Status**: Check remaining requests at `/api/rate-limit-status`
- **Frontend**: Built-in rate limit display and error handling

### Microservice Architecture

This application runs as a **microservice** behind your main website's nginx configuration:

```
Main Website (www.divyanshgandhi.com)
├── nginx handles SSL & routing
├── /introspect → Introspect AI Frontend (port 8080)
└── /introspect/api → Introspect AI Backend (port 8010)
```

## Environment Setup

Create a `.env` file:
```bash
cp environment.example .env
# Edit .env with your API keys
```

## Documentation

- 📖 **[Complete Documentation](docs/README.md)** - Detailed setup and usage instructions
- 🚀 **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- 🔧 **[Integration Guide](docs/change-request.md)** - Main website integration steps
- 📋 **[Product Requirements](docs/prd.md)** - Product specification and design
- 🏗️ **[Engineering Design](docs/ed.md)** - Technical implementation details
- 📁 **[Repository Structure](docs/STRUCTURE.md)** - Organization and architecture overview

## Project Structure

```
introspect-ai/
├── backend/              # Python FastAPI backend with Agno agents
│   ├── agents/           # Agent implementation using Agno
│   ├── api/              # FastAPI application
│   │   ├── main.py       # FastAPI app with rate limiting middleware
│   │   ├── routes.py     # API endpoints with rate limiting
│   │   ├── models.py     # Pydantic models
│   │   └── rate_limiter.py # Rate limiting implementation
│   ├── tests/            # Backend unit and integration tests
│   ├── infra/            # Infrastructure configuration
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Backend container configuration
├── frontend/             # React TypeScript frontend
│   ├── src/              # React application source
│   ├── package.json      # Node.js dependencies
│   └── Dockerfile.prod   # Production frontend container
├── docs/                 # All documentation
│   ├── README.md         # Detailed documentation
│   ├── prd.md            # Product Requirements Document
│   ├── ed.md             # Engineering Design Document
│   ├── DEPLOYMENT.md     # Deployment instructions
│   └── change-request.md # Main website integration guide
├── scripts/              # Utility scripts
│   ├── test-local.sh     # Local testing script
│   ├── run_test.sh       # Backend testing script
│   ├── test_rate_limiting.sh # Rate limiting test script
│   └── test_frontend_rate_limiting.sh # Frontend rate limiting test
├── deploy.sh             # Production deployment
├── dev.sh                # Development setup
├── start.sh              # Container startup script
└── docker-compose*.yml   # Container configurations
```

## Tech Stack

- **Backend**: Python, FastAPI, Agno framework, Gemini API
- **Frontend**: React, TypeScript, Vite, shadcn/ui
- **Infrastructure**: Docker, nginx (microservice mode)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

For detailed information, see the [complete documentation](docs/README.md). 