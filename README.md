# Documentation Template

This is a white-label documentation template. Follow the steps below to customize it with your brand.

## Quick Start

### Step 1: Create Your Repository

1. Click the green **"Use this template"** button (do NOT fork)
2. Choose a name for your documentation repository
3. Select whether it should be public or private
4. Click **"Create repository from template"**

### Step 2: Rebrand Your Documentation

1. Go to the **Actions** tab in your new repository
2. Click on **"Rebrand Documentation"** in the left sidebar
3. Click the **"Run workflow"** button
4. Fill in your branding details:
   - **Brand name**: Your company name (e.g., "MyCompany")
   - **Primary color**: Your brand color in hex (e.g., "#3B82F6")
   - **Website URL**: Your main website (e.g., "https://mycompany.com")
   - **Dashboard URL**: Your app/dashboard URL (e.g., "https://app.mycompany.com")
   - **Support URL**: Your contact/support page (e.g., "https://mycompany.com/contact")
   - **LinkedIn URL**: (Optional) Your LinkedIn company page
   - **OG Image URL**: (Optional) Your social sharing image URL
5. Click **"Run workflow"**
6. Wait for the workflow to complete (usually 1-2 minutes)

### Step 3: Add Your Logo

Replace the following files with your own logos:

- `resources/logo/dark.png` - Logo for dark mode
- `resources/logo/light.png` - Logo for light mode  
- `favicon.png` - Browser favicon

### Step 4: Connect to Mintlify

1. Go to [Mintlify Dashboard](https://dashboard.mintlify.com)
2. Create a new project or connect your repository
3. Install the Mintlify GitHub App when prompted
4. Your docs will automatically deploy on each push

## Syncing Updates

When new documentation updates are available from the upstream template:

1. Go to the **Actions** tab
2. Click on **"Sync Updates from Upstream"**
3. Click **"Run workflow"**
4. Enter the upstream repository name (provided by your platform provider)
5. Type `update` to confirm
6. Click **"Run workflow"**

The sync will:
- Fetch the latest content from the upstream template
- Preserve your branding configuration, logos, and favicon
- Re-apply your branding to the new content
- Commit the changes automatically

## Local Development

To preview documentation changes locally:

1. Install the [Mintlify CLI](https://www.npmjs.com/package/mintlify):
   ```bash
   npm i -g mintlify
   ```

2. Run the development server:
   ```bash
   mintlify dev
   ```

3. Open http://localhost:3000 in your browser

## File Structure

```
├── .github/workflows/     # GitHub Actions for rebranding and syncing
├── resources/logo/        # Your logo files (dark.png, light.png)
├── brand.config.json      # Your saved branding configuration
├── mint.json              # Mintlify configuration
├── favicon.png            # Browser favicon
└── [content folders]/     # Documentation content (.mdx files)
```

## Customizing Content

- Edit `.mdx` files to modify documentation content
- Update `mint.json` to change navigation structure
- Add new pages by creating `.mdx` files and adding them to `mint.json`

## Troubleshooting

- **Mintlify dev isn't running**: Run `mintlify install` to re-install dependencies
- **Page loads as 404**: Make sure you're running in the folder containing `mint.json`
- **Workflow fails**: Check the Actions log for error details
- **Branding not applied**: Ensure you ran the "Rebrand Documentation" workflow first

### Sync Workflow Permission Error

If you see an error like `refusing to allow a GitHub App to create or update workflow`, you need to manually update your workflow files:

**Step 1:** Go to the template repository workflow files:
- [sync-updates.yml](https://github.com/Autocalls/documentation/blob/main/.github/workflows/sync-updates.yml)
- [rebrand.yml](https://github.com/Autocalls/documentation/blob/main/.github/workflows/rebrand.yml)

**Step 2:** For each file:
1. Click the **"Raw"** button
2. Select all and copy (Ctrl+A, Ctrl+C)

**Step 3:** In your repository:
1. Go to `.github/workflows/sync-updates.yml`
2. Click the **pencil icon** (Edit)
3. Delete all content and paste the new content
4. Click **"Commit changes"**
5. Repeat for `rebrand.yml`

**Step 4:** Run the "Sync Updates" workflow again - it should work now

## Support

For platform-related questions, contact your platform provider.
For Mintlify-specific issues, visit [Mintlify Documentation](https://mintlify.com/docs).
