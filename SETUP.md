# Setup Guide

This guide will help you set up the Dropout Newsletter RSS Transformer with GitHub Actions and GitHub Pages.

## Prerequisites

- A GitHub account
- A Kill The Newsletter RSS feed URL for Dropout newsletter

## Step 1: Configure GitHub Pages

1. Go to your repository on GitHub
2. Click on **Settings** → **Pages**
3. Under **Build and deployment**, set:
   - **Source**: GitHub Actions
4. Save the settings

## Step 2: Add the Secret RSS Feed URL

The source RSS feed URL should be kept private as a GitHub secret.

1. Go to your repository on GitHub
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secret:
   - **Name**: `KILL_THE_NEWSLETTER_URL`
   - **Value**: Your Kill The Newsletter feed URL (e.g., `https://kill-the-newsletter.com/feeds/l9309dnw549798oyaxmv.xml`)
5. Click **Add secret**

## Step 3: Trigger the Workflow

The workflow will run automatically:
- Every 6 hours (via cron schedule - 4 times per day)
- When you push to the main branch
- When you manually trigger it

To manually trigger the workflow:

1. Go to **Actions** tab in your repository
2. Select **Update RSS Feeds** workflow
3. Click **Run workflow**
4. Select the branch (usually `main`)
5. Click **Run workflow**

## Step 4: Access Your Feeds

After the workflow runs successfully, your feeds will be available at:

```
https://[your-username].github.io/[repository-name]/
```

For example:
- All shows: `https://[your-username].github.io/[repository-name]/all-shows.xml`
- Dimension 20: `https://[your-username].github.io/[repository-name]/dimension-20.xml`
- Game Changer: `https://[your-username].github.io/[repository-name]/game-changer.xml`

## Step 5: Subscribe in Your RSS Reader

Copy any feed URL and add it to your favorite RSS reader:
- Feedly
- NewsBlur
- NetNewsWire
- Reeder
- Any other RSS reader

## Troubleshooting

### Workflow Fails with "Error: No Kill The Newsletter URL provided"

- Make sure you've added the `KILL_THE_NEWSLETTER_URL` secret correctly
- Check that the secret name is exactly `KILL_THE_NEWSLETTER_URL` (case-sensitive)

### Pages Not Deploying

- Verify that GitHub Pages is enabled and set to "GitHub Actions" source
- Check the Actions tab for any workflow errors
- Ensure the workflow completed successfully

### No Feeds Generated

- Check that your Kill The Newsletter feed URL is correct and accessible
- Verify the feed contains content
- Check the workflow logs for any errors during transformation

## Local Testing (Optional)

To test the transformer locally before deploying:

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` and add your feed URL
5. Run the transformer:
   ```bash
   python transform.py
   ```
6. Check the `feeds/` directory for generated XML files

## Security Notes

- The `KILL_THE_NEWSLETTER_URL` secret is never exposed in logs or output
- The secret is only accessible to GitHub Actions workflows
- Generated RSS feeds are public (they don't contain the source URL)
- Never commit the `.env` file to the repository
