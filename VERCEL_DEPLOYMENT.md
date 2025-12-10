# Deploying Moodify to Vercel

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git Repository**: Push your project to GitHub
3. **Spotify Credentials**: Have your Spotify Client ID and Client Secret ready

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

Make sure all changes are committed:
```bash
git add .
git commit -m "Add Vercel deployment configuration"
git push origin main
```

### Step 2: Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Select "Import Git Repository"
4. Connect your GitHub account and select your `moodstream` repository
5. Framework preset: Select "Other" (it's a Python Flask app)

### Step 3: Set Environment Variables

In the Vercel project settings:

1. Go to **Settings → Environment Variables**
2. Add the following variables:
   - `SPOTIFY_CLIENT_ID`: Your Spotify Client ID
   - `SPOTIFY_CLIENT_SECRET`: Your Spotify Client Secret
   - `FLASK_SECRET`: Generate a secure secret key (e.g., `python -c "import secrets; print(secrets.token_hex(32))"`)

### Step 4: Configure Vercel Build

Vercel should automatically detect the Python project. If not:

1. Build Command: (Leave empty - Vercel handles it)
2. Output Directory: (Leave empty)
3. Install Command: (Leave empty)

### Step 5: Deploy

Click "Deploy" and wait for the deployment to complete.

## Important Notes

- **Session Storage**: The app uses filesystem-based sessions. For production, consider using a database-backed session store (Redis, MongoDB, etc.)
- **Spotify Callback URL**: After deployment, update your Spotify app settings with the new callback URL: `https://your-vercel-domain.vercel.app/callback`
- **Requirements.txt**: All dependencies are listed in `requirements.txt`
- **Vercel.json**: Configuration is set up in `vercel.json` for proper routing

## Troubleshooting

### "Module not found" errors
- Ensure all imports use relative imports from the parent directory
- Check that the `routes/` folder has an `__init__.py` file

### Callback URL issues
- Update Spotify app redirect URI in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- The app automatically adjusts the redirect URI based on the Vercel deployment URL

### Session issues
- For production with multiple instances, migrate to a persistent session backend

## Local Testing

To test locally:
```bash
python -m pip install -r requirements.txt
python app.py
```

Then visit `http://localhost:5000`
