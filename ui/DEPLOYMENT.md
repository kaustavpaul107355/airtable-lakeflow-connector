# Deployment Guide

## Quick Start for Databricks Apps

### 1. Build the Application

```bash
# Install dependencies
npm install

# Build for production
npm run build
```

This creates an optimized build in the `dist/` directory.

### 2. File Structure After Build

```
dist/
├── index.html          # Main HTML file
├── assets/
│   ├── index-[hash].js    # Bundled JavaScript
│   └── index-[hash].css   # Bundled CSS
└── ...other assets
```

### 3. Databricks Apps Deployment

#### Option A: Direct Upload

1. Navigate to your Databricks workspace
2. Go to Apps section
3. Create a new app
4. Upload the contents of the `dist/` folder
5. Configure environment variables (if needed)
6. Deploy

#### Option B: Git Integration

1. Push code to a Git repository
2. In Databricks Apps, connect to your repository
3. Set build command: `npm run build`
4. Set output directory: `dist`
5. Deploy

### 4. Environment Configuration

If you need to use actual API keys (not recommended for client-side apps), create a `.env` file:

```env
VITE_AIRTABLE_API_KEY=your_key_here
VITE_DATABRICKS_TOKEN=your_token_here
```

**⚠️ Security Warning**: Never expose sensitive API keys in client-side code. Use a backend proxy instead.

### 5. Backend Integration (Recommended)

For production, you should proxy sensitive API calls through a backend:

```
Client (React App) → Backend API → Airtable/Databricks
```

Create API endpoints in Databricks:

```python
# Example backend endpoints
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/airtable/connect', methods=['POST'])
def connect_airtable():
    # Validate Airtable connection
    # Store credentials securely
    pass

@app.route('/api/sync/start', methods=['POST'])
def start_sync():
    # Trigger Lakeflow sync job
    # Return job ID for monitoring
    pass

@app.route('/api/sync/status/<job_id>', methods=['GET'])
def get_sync_status(job_id):
    # Check sync job status
    pass
```

### 6. Update API Calls in Components

Replace mock functions with actual API calls:

```typescript
// Example: SourceConfiguration.tsx
const handleConnect = async () => {
  try {
    const response = await fetch('/api/airtable/connect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        apiKey: apiKey,
        baseId: baseId
      })
    });
    
    if (response.ok) {
      setIsConnected(true);
      onConnect(true);
    }
  } catch (error) {
    console.error('Connection failed:', error);
  }
};
```

### 7. Testing Before Deployment

```bash
# Run local development server
npm run dev

# Test production build locally
npm run build
npm run preview
```

### 8. Post-Deployment Checks

- [ ] Verify all tabs load correctly
- [ ] Test connection workflows
- [ ] Verify visual flow animations
- [ ] Test table selection and navigation
- [ ] Check transformation mode switching
- [ ] Verify sync configuration options

### 9. Monitoring and Logs

Set up monitoring for:
- API call success/failure rates
- Sync job completion times
- Error rates by component
- User interaction patterns

### 10. Performance Optimization

The app is already optimized with:
- ✅ Code splitting
- ✅ Tree shaking
- ✅ Minification
- ✅ CSS optimization
- ✅ Lazy loading where appropriate

## Troubleshooting

### Build Issues

**Problem**: `npm run build` fails
```bash
# Clear cache and rebuild
rm -rf node_modules dist
npm install
npm run build
```

**Problem**: TypeScript errors
```bash
# Check types without building
npm run type-check
```

### Deployment Issues

**Problem**: App loads but shows blank screen
- Check browser console for errors
- Verify `index.html` is being served
- Check that asset paths are correct

**Problem**: Environment variables not loading
- Verify `.env` file format
- Restart development server
- Rebuild application

### Runtime Issues

**Problem**: API calls failing
- Check network tab in browser dev tools
- Verify backend endpoints are accessible
- Check CORS configuration

## Production Checklist

- [ ] Remove all console.log statements
- [ ] Replace mock data with real API calls
- [ ] Configure error boundaries
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Enable HTTPS only
- [ ] Configure proper CORS policies
- [ ] Set up authentication
- [ ] Add rate limiting
- [ ] Configure caching headers
- [ ] Minify and compress assets
- [ ] Enable gzip/brotli compression
- [ ] Set up CDN (if needed)
- [ ] Configure monitoring and alerts
- [ ] Test on multiple browsers
- [ ] Test on mobile devices
- [ ] Perform security audit
- [ ] Document API endpoints
- [ ] Create user documentation

## Rollback Plan

If deployment fails:

1. Keep previous version available
2. Monitor error rates
3. Have rollback script ready:
   ```bash
   # Example rollback
   git revert <commit-hash>
   npm run build
   # Redeploy
   ```

## Support

For deployment issues:
- Check Databricks Apps documentation
- Review build logs
- Contact Databricks support

## Next Steps

After successful deployment:
1. Monitor application performance
2. Gather user feedback
3. Plan iterative improvements
4. Set up automated testing
5. Implement CI/CD pipeline
