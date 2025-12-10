# Deploying Moodify to Netlify

## Prerequisites

1. **Netlify Account**: Sign up at [netlify.com](https://netlify.com)
2. **Git Repository**: Push your project to GitHub (already done ✓)
3. **Spotify Credentials**: Have your Spotify Client ID and Client Secret ready

## Step-by-Step Deployment

### Step 1: Push Latest Changes to GitHub

```bash
git add netlify.toml api/handler.py
git commit -m "Add Netlify deployment configuration"
git push origin main
```

### Step 2: Connect to Netlify

1. Go to [netlify.com](https://netlify.com)
2. Click "Add new site" → "Import an existing project"
3. Choose "GitHub" as your Git provider
4. Select your `moodstream` repository
5. Click "Deploy site"

### Step 3: Configure Build Settings

Netlify should auto-detect your settings. If not, configure:
- **Base directory**: (leave empty)
- **Build command**: `pip install -r requirements.txt`
- **Functions directory**: `api`
- **Publish directory**: `.` (root)

### Step 4: Set Environment Variables

1. Go to **Site settings** → **Build & deploy** → **Environment**
2. Add the following environment variables:
   - `SPOTIFY_CLIENT_ID`: Your Spotify Client ID
   - `SPOTIFY_CLIENT_SECRET`: Your Spotify Client Secret
   - `FLASK_SECRET`: Your generated Flask secret key

### Step 5: Deploy

Click "Deploy site" and wait for the build to complete. Netlify will automatically rebuild on every push to main.

## Important Notes

- **Netlify Functions**: Your Flask app runs as a serverless function in `api/handler.py`
- **Session Storage**: The app uses filesystem-based sessions. For production, consider using a database backend (Redis, MongoDB, etc.)
- **Spotify Callback URL**: After deployment, update your Spotify app settings with the new callback URL: `https://your-netlify-domain.netlify.app/callback`

## Troubleshooting

### Build Fails
- Check the **Deploys** tab for build logs
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### Import Errors
- Check that all relative imports are correct
- Ensure the `routes/` folder has an `__init__.py` file

### Callback URL Issues
- Update your Spotify Developer Dashboard with the correct callback URL
- The URL format is: `https://your-site-name.netlify.app/callback`

## Local Testing

```bash
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000`
