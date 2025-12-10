# Supabase Setup Guide for VolunteerConnect Hub

This guide walks you through setting up Supabase for production use with VolunteerConnect Hub.

## Prerequisites

- A GitHub account
- The VolunteerConnect Hub repository cloned

## Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/sign in
2. Click **"New Project"**
3. Configure your project:
   - **Name**: `volunteerconnect-hub`
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose one closest to your users
4. Click **"Create new project"**
5. Wait for the project to be provisioned (1-2 minutes)

## Step 2: Set Up Authentication

### Enable Email/Password Auth
1. Go to **Authentication** → **Providers**
2. Email provider should be enabled by default
3. Configure settings:
   - Enable "Confirm email" (recommended for production)
   - Set "Minimum password length" to 8+

### Enable Google OAuth
1. Go to **Authentication** → **Providers** → **Google**
2. Toggle **Enable Google provider**
3. You'll need OAuth credentials from Google Cloud Console:

#### Getting Google OAuth Credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Go to **APIs & Services** → **Credentials**
4. Click **"Create Credentials"** → **"OAuth client ID"**
5. Configure the consent screen if prompted
6. Choose **"Web application"**
7. Add authorized redirect URI from Supabase (shown in Supabase dashboard)
8. Copy the **Client ID** and **Client Secret**
9. Paste them in Supabase

### Configure URL Settings
1. Go to **Authentication** → **URL Configuration**
2. Set **Site URL**: `https://pythpythpython.github.io/volunteer-connect-hub/`
3. Add **Redirect URLs**:
   - `https://pythpythpython.github.io/volunteer-connect-hub/`
   - `http://localhost:4000/volunteer-connect-hub/` (for local development)

## Step 3: Create Database Tables

1. Go to **SQL Editor**
2. Click **"New query"**
3. Copy the entire contents of **`supabase_schema.sql`** (in the repo root)
4. Paste and run the SQL
5. Verify tables were created in **Table Editor**

> **IMPORTANT**: Use `supabase_schema.sql`, NOT the SQL from `database_board.py`. 
> The schema file has tables in the correct order to handle foreign key dependencies.

The schema creates these tables:
- `profiles` - User profile data (linked to auth.users)
- `hours_log` - Volunteer hours tracking
- `events` - Scheduled volunteer events
- `letters` - Generated letters and applications
- `applications` - Volunteer applications
- `opportunities` - Volunteer opportunities
- `recommendations` - Personalized recommendations

## Step 4: Get API Keys

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key (safe for frontend)
   - **service_role** key (keep secret - for server-side only)

## Step 5: Update Frontend Code

Edit `assets/js/database.js`:

```javascript
const SUPABASE_URL = 'https://YOUR_PROJECT.supabase.co';
const SUPABASE_ANON_KEY = 'your-anon-key-here';
```

## Step 6: Configure GitHub Secrets

For GitHub Actions (data backup, opportunity crawling):

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `SUPABASE_URL`: Your project URL
   - `SUPABASE_SERVICE_KEY`: Your service_role key (NOT the anon key)

## Step 7: Test the Setup

1. Build and run the site locally:
   ```bash
   bundle exec jekyll serve
   ```
2. Open `http://localhost:4000/volunteer-connect-hub/`
3. Try signing up with email
4. Try signing in with Google
5. Complete the profile questionnaire
6. Verify data appears in Supabase Table Editor

## Security Checklist

- [ ] Row Level Security (RLS) is enabled on all tables
- [ ] Only `anon` key is used in frontend code
- [ ] `service_role` key is only in GitHub Secrets
- [ ] Google OAuth redirect URLs are correct
- [ ] Email confirmations are enabled
- [ ] Strong password requirements are set

## Troubleshooting

### "Invalid API key" error
- Make sure you're using the `anon` key, not the `service_role` key
- Check that the key is correctly copied without extra spaces

### Google Sign-In not working
- Verify redirect URLs in both Google Console and Supabase
- Check browser console for specific error messages

### Data not persisting
- Check browser console for Supabase errors
- Verify RLS policies allow the operation
- Test policies in Supabase SQL Editor

### Profile not saving
- The profile is automatically created on signup via database trigger
- Check that the `handle_new_user()` trigger exists

## Cost Considerations

Supabase Free Tier includes:
- 500MB database storage
- 2GB bandwidth
- 50,000 monthly active users
- Unlimited API requests

This is more than enough for most volunteer organizations. Upgrade only if you exceed these limits.

## Support

- [Supabase Documentation](https://supabase.com/docs)
- [VolunteerConnect Hub Issues](https://github.com/pythpythpython/volunteer-connect-hub/issues)
