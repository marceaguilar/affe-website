# Working Papers Submission Setup Guide

This guide will walk you through setting up the Google Form for working paper submissions and connecting it to your website.

## Step 1: Create a Google Form

1. Go to [Google Forms](https://forms.google.com)
2. Click **"+ Blank"** to create a new form
3. Title it: **"Working Paper Submission"** (or similar)

## Step 2: Add Form Fields

Add the following fields in order:

### Field 1: Paper Title
- **Type:** Short answer text
- **Question:** "Paper Title"
- **Required:** ✓ Yes

### Field 2: Authors
- **Type:** Paragraph (or Short answer if you prefer)
- **Question:** "Authors"
- **Description:** "Enter all author names, separated by commas (e.g., John Doe, Jane Smith, Bob Johnson)"
- **Required:** ✓ Yes

### Field 3: Universities/Affiliations
- **Type:** Paragraph (or Short answer if you prefer)
- **Question:** "Universities" or "Universities/Affiliations"
- **Description:** "Enter the university or affiliation for each author, separated by commas in the same order as authors"
- **Required:** ✓ Yes

### Field 4: Abstract (Optional)
- **Type:** Paragraph
- **Question:** "Abstract"
- **Description:** "Brief description or abstract of your working paper (optional)"
- **Required:** ✗ No

### Field 5: PDF Upload
- **Type:** File upload
- **Question:** "PDF Upload" or "Upload Your Paper"
- **Description:** "Upload your working paper as a PDF file"
- **Required:** ✓ Yes
- **Settings:** 
  - Maximum file size: Set as needed (e.g., 10 MB or 50 MB)
  - Accepted file types: PDF only (you can specify this in advanced settings)

### Field 6: Timestamp (Auto-generated)
- This will be automatically added by Google Forms - no need to create it manually

## Step 3: Link Form to Google Sheet

1. In your Google Form, click the **"Responses"** tab at the top
2. Click the green **Google Sheets icon** 📊 (or the text "Link to Sheets")
3. Choose:
   - **"Create a new spreadsheet"** (recommended for first time)
   - Or **"Select existing spreadsheet"** if you already have one set up
4. Click **"Create"** or **"Select"**

This creates/links a Google Sheet where all submissions will be stored.

## Step 4: Publish Google Sheet to Web (CSV)

1. Open the linked Google Sheet
2. Go to **File → Share → Publish to web**
3. In the dialog:
   - **What to publish:** Select the sheet/tab name (usually "Form Responses 1")
   - **Format:** Select **"CSV"**
   - Check **"Automatically republish when changes are made"**
4. Click **"Publish"**
5. Copy the generated URL (it will look like: `https://docs.google.com/spreadsheets/d/.../export?format=csv&gid=...`)

## Step 5: Update Website Configuration

### A. Update `_config.yml`

Edit `_config.yml` and ensure the `working_papers_url` points to your published CSV:

```yaml
google_sheets:
  working_papers_url: "PASTE_YOUR_CSV_URL_HERE"
```

Replace `PASTE_YOUR_CSV_URL_HERE` with the URL you copied in Step 4.

### B. Get Google Form Embed URL

1. In your Google Form, click the **"Send"** button (top right)
2. Click the **"<>"** icon (Embed HTML)
3. Copy the **src** URL from the iframe code (or copy the entire iframe and extract the src)
   - It will look like: `https://docs.google.com/forms/d/e/.../viewform?embedded=true`
4. **Note:** Make sure the form allows public submissions (Settings → Responses → "Accepting responses" should be ON)

### C. Update `pages/submit-working-paper.md`

Edit `pages/submit-working-paper.md` and add the embed URL to the front matter:

```yaml
---
layout: submit-working-paper
title: Submit Working Paper
permalink: /submit-working-paper
google_form_url: "PASTE_YOUR_EMBED_URL_HERE"
---
```

Replace `PASTE_YOUR_EMBED_URL_HERE` with the embed URL from Step 5B.

## Step 6: Verify Column Names in Google Sheet

After receiving a test submission, check your Google Sheet column names. The website script will automatically match these variations:

**Title fields:**
- `Paper Title`, `Title`, `title`, `Name`, `Paper Name`

**Author fields:**
- `Authors`, `Author`, `Full Name (Presenting Author)`, `Author Name`, `author`, `authors`, `Your Name`, `Name`

**University/Affiliation fields:**
- `Universities`, `University`, `Universities/Affiliations`, `Affiliation / University`, `Affiliation`, `Affiliations`, `Institution`, `Institutions`, `affiliation`, `University/Affiliation`, `Organization`

**PDF/Link fields:**
- `PDF Upload`, `Link`, `Paper Link`, `URL`, `Download Link`, `PDF Link`

**Date fields:**
- `Timestamp`, `Marca temporal`, `Date Submitted`, `timestamp`, `Submit Time`

If your Google Form creates columns with different names, you can either:
1. Rename the columns in Google Sheets to match one of the supported names above, OR
2. Modify the field matching logic in `assets/js/working-papers.js` (lines 98-105)

## Step 7: Test the Setup

1. Visit your website at `/submit-working-paper`
2. Fill out and submit a test working paper
3. Check that it appears in your Google Sheet
4. Visit `/working-papers` and verify the paper appears correctly

## Troubleshooting

### Papers not showing on website
- ✅ Verify Google Sheet is published (Step 4)
- ✅ Check the CSV URL in `_config.yml` is correct
- ✅ Ensure column names match expected variations (see Step 6)
- ✅ Check browser console for JavaScript errors

### Form not appearing
- ✅ Verify `google_form_url` is set in `pages/submit-working-paper.md`
- ✅ Check the embed URL is correct (should end with `viewform?embedded=true`)
- ✅ Ensure form accepts responses (Form Settings → Responses)

### File upload issues
- ✅ Check Google Form file upload size limits
- ✅ Verify users have permission to upload files
- ✅ Ensure PDF file type is selected/allowed

## Google Sheet Column Format Recommendation

For best compatibility, your Google Sheet should have columns like:

| Paper Title | Authors | Universities | Abstract | PDF Upload | Timestamp |
|------------|---------|--------------|----------|------------|-----------|
| Example Title | John Doe, Jane Smith | Harvard, MIT | Abstract text... | [link] | 1/15/2025 10:30:00 |

The script will automatically handle variations, but using these exact names ensures the best experience.
