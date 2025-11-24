---
layout: default
title: Posted Working Papers
---

<h1 class="page-title">Posted Working Papers</h1>

<div id="working-papers-container" class="working-papers-container">
  <div class="papers-loading">Loading working papers...</div>
</div>

<script>
  // Load working papers on page load
  document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('working-papers-container');
    
    const sheetsUrl = '{{ site.google_sheets.working_papers_url }}';
    
    if (!sheetsUrl || sheetsUrl.trim() === '') {
      container.innerHTML = `
        <div class="papers-error">
          <p><strong>Google Sheets URL not configured.</strong></p>
          <p>To display working papers from your Google Form:</p>
          <ol>
            <li>Open your Google Sheet (linked to the form)</li>
            <li>Go to File → Share → Publish to web</li>
            <li>Select "CSV" format and click "Publish"</li>
            <li>Copy the generated URL</li>
            <li>Add it to <code>_config.yml</code> under <code>google_sheets.working_papers_url</code></li>
          </ol>
          <p>Expected columns in your Google Sheet: Title, Author, Abstract, Link, Timestamp</p>
        </div>
      `;
      return;
    }

    fetch(sheetsUrl)
      .then(response => {
        if (!response.ok) throw new Error('Failed to fetch data');
        return response.text();
      })
      .then(csvText => {
        const papers = parseCSV(csvText);
        displayPapers(papers, container);
      })
      .catch(error => {
        container.innerHTML = `
          <div class="papers-error">
            <p>Error loading working papers: ${error.message}</p>
            <p>Please check your Google Sheets URL and ensure the sheet is published to the web.</p>
          </div>
        `;
      });
  });

  function parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    if (lines.length < 2) return [];
    
    const headers = parseCSVLine(lines[0]);
    const papers = [];
    
    for (let i = 1; i < lines.length; i++) {
      const values = parseCSVLine(lines[i]);
      if (values.length === 0 || values.every(v => !v.trim())) continue;
      
      const paper = {};
      headers.forEach((header, index) => {
        paper[header.trim()] = values[index] ? values[index].trim() : '';
      });
      papers.push(paper);
    }
    
    return papers;
  }

  function parseCSVLine(line) {
    const values = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      
      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (char === ',' && !inQuotes) {
        values.push(current);
        current = '';
      } else {
        current += char;
      }
    }
    values.push(current);
    
    return values;
  }

  function displayPapers(papers, container) {
    if (papers.length === 0) {
      container.innerHTML = '<div class="papers-loading">No working papers found.</div>';
      return;
    }

    const papersList = document.createElement('ul');
    papersList.className = 'papers-list';

    papers.forEach(paper => {
      const paperItem = document.createElement('li');
      paperItem.className = 'paper-item';
      
      // Flexible field matching
      const title = paper['Paper Title'] || paper['Title'] || paper['title'] || 
                   paper['Name'] || paper['Paper Name'] || 'Untitled';
      const author = paper['Author'] || paper['Author Name'] || paper['author'] || 
                    paper['Your Name'] || paper['Name'] || 'Unknown';
      const abstract = paper['Abstract'] || paper['Description'] || paper['abstract'] || 
                      paper['Summary'] || '';
      const date = paper['Timestamp'] || paper['Date Submitted'] || paper['timestamp'] || 
                  paper['Submit Time'] || '';
      const link = paper['Link'] || paper['Paper Link'] || paper['URL'] || 
                  paper['Download Link'] || paper['PDF Link'] || '';
      
      let dateDisplay = '';
      if (date) {
        try {
          const dateObj = new Date(date);
          dateDisplay = dateObj.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          });
        } catch (e) {
          dateDisplay = date;
        }
      }

      const titleHtml = link ? 
        `<a href="${link}" target="_blank" rel="noopener noreferrer">${escapeHtml(title)}</a>` : 
        escapeHtml(title);

      paperItem.innerHTML = `
        <div class="paper-title">${titleHtml}</div>
        <div class="paper-author">${escapeHtml(author)}</div>
        ${dateDisplay ? `<div class="paper-date">Submitted: ${dateDisplay}</div>` : ''}
        ${abstract ? `<div class="paper-abstract">${escapeHtml(abstract)}</div>` : ''}
      `;

      papersList.appendChild(paperItem);
    });

    container.innerHTML = '';
    container.appendChild(papersList);
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
</script>

