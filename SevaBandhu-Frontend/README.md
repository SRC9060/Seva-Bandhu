# Seva Bandhu Frontend

This folder now contains the Vite + React frontend foundation for Vercel.

## Deploy to Vercel

1. Import the SRC9060/Seva-Bandhu GitHub repository into Vercel.
2. Select the branch feature/vercel-frontend-foundation for the preview deployment.
3. Set the project Root Directory to SevaBandhu-Frontend.
4. Use the Vite framework preset, Build Command npm run build, and Output Directory dist.
5. Add the environment variable VITE_BACKEND_URL with the value https://seva-bandhu-src9060.onrender.com.
6. Deploy and test the landing page and its portal links on mobile and desktop.

Vercel's automatic deployment will use this folder's package.json and vite.config.js. The matching settings are also recorded in vercel.json.

## Current integration boundary

This is the first Vercel frontend slice. The React landing page links to the existing Django-rendered customer, technician and admin flows on Render. Those pages, sessions, server-side forms and current WebSocket features remain on Render while the standalone frontend is migrated incrementally. Do not assume this is already a full React replacement for every Django template.

The deployed backend is configured by VITE_BACKEND_URL. This value is public frontend configuration, not a secret. Never place database passwords, Django secret keys, payment secrets or service-role keys in VITE-prefixed variables.

## Local development

Install Node.js 20.19 or newer, then run npm install and npm run dev from this folder. Use npm run build to create the production assets in dist.
