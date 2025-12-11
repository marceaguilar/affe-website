# AFFE Website

A Jekyll-based GitHub Pages website for AFFE (Accounting and Finance Field Experiments) conference group.

## Features

- **Posted Working Papers**: Integrates with Google Sheets to display working papers submitted via Google Form
- **Announcements**: Timeline view of announcements
- **Conference Postings**: Current conference information
- **Registration**: Form to register for group updates
- **About Section**: Information about the group and organizing committee
- **Past Conferences**: Links to previous conference websites

## Setup

### 1. Install Dependencies

```bash
bundle install
```

### 2. Configure Google Sheets Integration

1. Create a Google Form for working paper submissions
2. Link it to a Google Sheet
3. Publish the Google Sheet to the web:
   - Go to File → Share → Publish to web
   - Select "CSV" format
   - Click "Publish"
   - Copy the generated URL
4. Add the URL to `_config.yml`:
   ```yaml
   google_sheets:
     working_papers_url: "YOUR_GOOGLE_SHEETS_CSV_URL"
   ```

### 3. Expected Google Sheet Columns

Your Google Sheet should have columns like:
- Title / Paper Title
- Author / Author Name
- Abstract / Description
- Link / Paper Link / URL (optional)
- Timestamp / Date Submitted

The script will automatically match common column name variations.

### 4. Add Content Data

Create YAML data files in `_data/` directory:

**`_data/announcements.yml`**:
```yaml
- date: "January 15, 2025"
  title: "Announcement Title"
  content: "Announcement content in markdown format"
```

**`_data/conferences.yml`**:
```yaml
- title: "Conference Name"
  date: "March 15-17, 2025"
  description: "Conference description"
  link: "https://conference-url.com"
  deadline: "Submission deadline: February 1, 2025"
```

**`_data/team.yml`**:
```yaml
- name: "Name"
  role: "Role/Title"
  institution: "Institution Name"
```

**`_data/past_conferences.yml`**:
```yaml
- title: "Conference Name"
  date: "March 2024"
  location: "Location"
  link: "https://conference-website.com"
```

### 5. Configure Registration Form

Update `register.md` with your Google Form details:
1. Get the form action URL from your Google Form
2. Get the entry field names (entry.XXXXXXX)
3. Update the form in `register.md`

Or embed the Google Form directly using an iframe.

### 6. Local Development

```bash
bundle exec jekyll serve
```

Visit `http://localhost:4000`

### 7. Deploy to GitHub Pages

1. Push this repository to GitHub
2. Go to repository Settings → Pages
3. Select the branch (usually `main` or `gh-pages`)
4. Select `/ (root)` as the source
5. The site will be available at `https://YOUR_USERNAME.github.io/REPO_NAME`

## Customization

### Color Palette

The site uses the following color palette (defined in `assets/css/main.css`):
- Parchment: #E8E5D7
- Olive: #B8B794
- Bark: #5A4A3A
- Sand: #D4C4A0
- Sage: #8FA88F
- Olivewood: #2D2B1F

### Site Configuration

Edit `_config.yml` to customize:
- Site title and description
- Navigation menu
- Google Sheets URLs
- Other Jekyll settings

## Notes

- The Google Sheets integration requires the sheet to be published to the web
- The CSV parser handles quoted values and commas within fields
- All pages are responsive and mobile-friendly
- The site follows Jekyll best practices for GitHub Pages

