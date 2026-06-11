# Deployment

Build the frontend with:

```bash
npm run build
```

Serve `dist/` behind HTTPS. Set:

```bash
VITE_API_URL=https://your-api-host
VITE_APP_NAME=NurseKonnect
VITE_MAP_PROVIDER=openstreetmap
```

Production deployments should enable secure cookies, CSP headers, HSTS, and same-site protections at the API and reverse proxy layers.

The SPA must route all unknown frontend paths back to `index.html` so protected and lazy-loaded routes work after refresh. Static assets in `dist/assets/` should be served with long-lived immutable cache headers.

Container deployment:

```bash
docker build -t nursekonnect-frontend .
docker run -p 8080:80 nursekonnect-frontend
```

The included `nginx.conf` serves the SPA, applies security headers, and enables immutable caching for built assets.
