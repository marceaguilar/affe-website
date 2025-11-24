# Quick Setup Guide

This guide will help you quickly set up your WEFIDEV website on GitHub Pages.

## Step 1: Install Dependencies

```bash
bundle install
```

## Step 2: Configure Google Sheets for Working Papers

1. **Create a Google Form** for paper submissions with fields like:
   - Paper Title
   - Author Name
   - Abstract
   - Link (optional)
   - Timestamp (auto-filled)

2. **Link it to a Google Sheet**

3. **Publish the Sheet to the web:**
   - Open your Google Sheet
   - Go to **File → Share → Publish to web**
   - Select format: **CSV**
   - Click **Publish**
   - Copy the generated URL

4. **Add the URL to `_config.yml`:**
   ```yaml
   google_sheets:
     working_papers_url: "YOUR_GOOGLE_SHEETS_CSV_URL"
   ```

## Step 3: Set Up Registration Form

1. Create a Google Form for registration
2. Click **Send** → Click the **<>** (embed) icon
3. Copy the iframe `src` URL
4. Edit `register.md`:
   - Uncomment the iframe code
   - Replace `YOUR_GOOGLE_FORM_EMBED_URL` with your URL
   - Remove the placeholder section

## Step 4: Add Content Data

Create data files in `_data/` directory (examples already provided):

### Announcements (`_data/announcements.yml`)
```yaml
- date: "January 15, 2025"
  title: "Announcement Title"
  content: "Content here"
```

### Conferences (`_data/conferences.yml`)
```yaml
- title: "Conference Name"
  date: "March 15-17, 2025"
  description: "Description"
  link: "https://conference-url.com"
  deadline: "Submission deadline: February 1, 2025"
```

### Team (`_data/team.yml`)
```yaml
- name: "Name"
  role: "Role/Title"
  institution: "Institution Name"
```

### Past Conferences (`_data/past_conferences.yml`)
```yaml
- title: "Conference Name"
  date: "March 2024"
  location: "Location"
  link: "https://conference-website.com"
```

## Step 5: Customize Site Information

Edit `_config.yml` to update:
- Site title and description
- Navigation menu items
- Google Sheets URLs

## Step 6: Test Locally

```bash
bundle exec jekyll serve
```

Visit `http://localhost:4000` to preview your site.

## Step 7: Deploy to GitHub Pages

1. Push your repository to GitHub
2. Go to **Settings → Pages**
3. Select your branch (usually `main` or `gh-pages`)
4. Select source: **/ (root)**
5. Your site will be available at `https://YOUR_USERNAME.github.io/REPO_NAME`

## Color Palette

The site uses these colors (defined in `assets/css/main.css`):
- **Parchment**: #E8E5D7 (background)
- **Olive**: #B8B794 (accent)
- **Bark**: #5A4A3A (text)
- **Sand**: #D4C4A0 (light accent)
- **Sage**: #8FA88F (primary)
- **Olivewood**: #2D2B1F (header/footer)

## Troubleshooting

### Working Papers Not Loading
- Check that your Google Sheet is published to the web
- Verify the CSV URL format is correct
- Ensure your sheet has a header row with column names
- Check browser console for errors

### Form Not Working
- Verify the iframe src URL is correct
- Make sure your Google Form allows public submissions
- Check that the form is set to accept responses

### Styles Not Loading
- Make sure `baseurl` in `_config.yml` matches your GitHub Pages path
- If using a custom domain or subpath, update the `baseurl`

## Next Steps

- Customize the color scheme in `assets/css/main.css`
- Update page content in individual `.md` files
- Add images to `assets/images/` and reference them in pages
- Customize the layout in `_layouts/default.html`

