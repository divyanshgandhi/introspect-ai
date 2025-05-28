# Introspect AI - Personal Knowledge Assistant

## Project Overview

Introspect AI is a personal knowledge assistant that helps you extract meaningful insights from various content sources and generate personalized action plans. The application allows you to:

1. Upload files or provide YouTube links as content sources
2. Add personal context (interests, goals, background)
3. Generate a personalized prompt that can be pasted into ChatGPT
4. Receive tailored recommendations based on the content and your specific context

## Project Structure

The frontend is built with a modern React architecture:

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── ui/          # Shadcn UI components
│   │   ├── FileUpload.tsx
│   │   ├── YouTubeInput.tsx
│   │   ├── UserContext.tsx
│   │   ├── ContentExtractor.tsx
│   │   ├── UploadPane.tsx
│   │   └── OutputPane.tsx
│   ├── pages/           # Application pages/routes
│   │   ├── Index.tsx    # Main application page
│   │   └── NotFound.tsx # 404 page
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utility functions and helpers
│   ├── App.tsx          # Main app component with routing
│   └── main.tsx         # Application entry point
```

## Technologies Used

This project is built with:

- **Vite** - Fast development server and build tool
- **TypeScript** - Type-safe JavaScript
- **React** - UI framework
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching and state management
- **Shadcn UI** - Component library based on Radix UI
- **Tailwind CSS** - Utility-first CSS framework

## How It Works

The application follows a "two-hop" architecture:

1. **Extract Phase**: Content from files or YouTube is processed to extract key insights
2. **Personalize Phase**: The extracted insights are combined with user context to generate a personalized prompt
3. **Output**: The final prompt can be copied and pasted into ChatGPT for tailored recommendations

## Getting Started

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

## Deployment

Simply open [Lovable](https://lovable.dev/projects/310bb355-f232-4719-81dc-f0c8b4646b4d) and click on Share -> Publish.

## Custom Domain Setup

Yes, you can connect a custom domain!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)

## Contributing

The codebase follows these conventions:
- Component structure: UI components are separated from logic
- Styling: Uses Tailwind CSS utility classes
- State management: React hooks for local state, TanStack Query for remote data

When making changes:
1. Follow the established component patterns
2. Ensure all code is typed properly with TypeScript
3. Maintain the clean separation between UI and business logic
