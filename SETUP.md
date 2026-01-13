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

## Step 2.5: Configure Timezone Adjustment (Optional)

If you want episode air times to be converted from Eastern Time (ET) to your local timezone, you can configure a timezone offset.

### For GitHub Actions

You have two options to configure timezone for GitHub Actions:

**Option A: Add as a Repository Variable (Recommended)**

1. Go to your repository on GitHub
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click on the **Variables** tab
4. Click **New repository variable**
5. Add the following variable:
   - **Name**: `TIMEZONE_OFFSET`
   - **Value**: Your timezone offset from ET in hours (e.g., `15` for AEST, `5` for UK BST)
6. Click **Add variable**
7. Update the workflow file `.github/workflows/update-feeds.yml` to use this variable (see below)

**Option B: Edit the Workflow File Directly**

1. Edit `.github/workflows/update-feeds.yml` in your repository
2. Find the "Transform RSS feed" step (around line 49)
3. Add the `--timezone-offset` parameter to the python command:
   ```yaml
   - name: Transform RSS feed
     env:
       KILL_THE_NEWSLETTER_URL: ${{ secrets.KILL_THE_NEWSLETTER_URL }}
     run: |
       python transform.py --output feeds --base-url "https://${{ github.repository_owner }}.github.io/${{ github.event.repository.name }}" --timezone-offset 15
   ```
4. Replace `15` with your desired offset
5. Commit and push the changes

**Using Repository Variable (for Option A)**

If you choose Option A, modify the "Transform RSS feed" step in `.github/workflows/update-feeds.yml`:

```yaml
- name: Transform RSS feed
  env:
    KILL_THE_NEWSLETTER_URL: ${{ secrets.KILL_THE_NEWSLETTER_URL }}
    TIMEZONE_OFFSET: ${{ vars.TIMEZONE_OFFSET }}
  run: |
    python transform.py --output feeds --base-url "https://${{ github.repository_owner }}.github.io/${{ github.event.repository.name }}" --timezone-offset $TIMEZONE_OFFSET
```

### Timezone Offset Examples

Calculate your offset from Eastern Time (ET):

**During US Daylight Saving Time (March - November):**
- **Australia (AEDT, UTC+11)**: `TIMEZONE_OFFSET=16`
- **Australia (AEST, UTC+10)**: `TIMEZONE_OFFSET=15`
- **Japan (JST, UTC+9)**: `TIMEZONE_OFFSET=14`
- **UK (BST, UTC+1)**: `TIMEZONE_OFFSET=5`
- **Brazil (BRT, UTC-3)**: `TIMEZONE_OFFSET=3`
- **No conversion (ET)**: `TIMEZONE_OFFSET=0`

**During US Standard Time (November - March):**
- **Australia (AEDT, UTC+11)**: `TIMEZONE_OFFSET=15`
- **Australia (AEST, UTC+10)**: `TIMEZONE_OFFSET=14`
- **Japan (JST, UTC+9)**: `TIMEZONE_OFFSET=13`
- **UK (GMT, UTC+0)**: `TIMEZONE_OFFSET=5`
- **Brazil (BRT, UTC-3)**: `TIMEZONE_OFFSET=2`
- **No conversion (ET)**: `TIMEZONE_OFFSET=0`

**Important Notes:**
- This is a simple hour-based offset and doesn't automatically adjust for daylight saving time changes
- You may need to update the offset when DST transitions occur (typically in March and November for the US)
- The timezone conversion will adjust both the time and the day of the week when the conversion crosses midnight

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
4. Edit `.env` and add your feed URL and optionally configure timezone:
   ```env
   KILL_THE_NEWSLETTER_URL=https://kill-the-newsletter.com/feeds/xxxxx.xml
   TIMEZONE_OFFSET=15  # Optional: Set your timezone offset (0 for no conversion)
   ```
5. Run the transformer:
   ```bash
   python transform.py
   ```
   Or with command-line timezone option:
   ```bash
   python transform.py --timezone-offset 15
   ```
6. Check the `feeds/` directory for generated XML files

For more details on timezone configuration, see the [README.md](README.md#timezone-configuration) file.

## Security Notes

- The `KILL_THE_NEWSLETTER_URL` secret is never exposed in logs or output
- The secret is only accessible to GitHub Actions workflows
- Generated RSS feeds are public (they don't contain the source URL)
- Never commit the `.env` file to the repository
