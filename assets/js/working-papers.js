// Static working papers data
const staticPapers = [
  {
    'Title': 'Paid Tax Preparers and Social Benefit Take-up: Evidence from a Field Experiment',
    'Authors': 'Andrew Belnap (University of Texas at Austin), Anthony Welsch (University of Chicago), Jeffrey Gramlich (Washington State University), Braden Williams (University of Texas at Austin)',
    'Link': '/assets/pdf/BGWW.pdf'
  },
  {
    'Title': 'Racial and Gender Favoritism in Crowdfunding—Evidence from the Field',
    'Authors': 'Ha Diep-Nguyen (Purdue University), Michael Price (University of Alabama, NBER, ANU), Jun Yang (Nanyang Technological University & Indiana University)',
    'Link': '/assets/pdf/DPY.pdf'
  }
];

// Load working papers on page load
document.addEventListener('DOMContentLoaded', function() {
  const container = document.getElementById('working-papers-container');
  if (!container) return;
  
  // Use static papers
  displayPapers(staticPapers, container);
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
  try {
    if (papers.length === 0) {
      container.innerHTML = '<div class="papers-loading">No working papers found.</div>';
      return;
    }

    const papersList = document.createElement('ul');
    papersList.className = 'papers-list';

    papers.forEach(paper => {
      try {
    const paperItem = document.createElement('li');
    paperItem.className = 'paper-card';
    
    // Flexible field matching
    const title = paper['Paper Title'] || paper['Title'] || paper['title'] || 
                 paper['Name'] || paper['Paper Name'] || 'Untitled';
    const author = paper['Authors'] || paper['Author'] || 
                  paper['Full Name (Presenting Author)'] || paper['Author Name'] || 
                  paper['author'] || paper['authors'] || paper['Your Name'] || 
                  paper['Name'] || 'Unknown';
    const affiliation = paper['Universities'] || paper['University'] || 
                       paper['Universities/Affiliations'] || paper['Affiliation / University'] || 
                       paper['Affiliation'] || paper['Affiliations'] || 
                       paper['Institution'] || paper['Institutions'] || 
                       paper['affiliation'] || paper['University/Affiliation'] || 
                       paper['Organization'] || '';
    const abstract = paper['Abstract'] || paper['Description'] || paper['abstract'] || 
                    paper['Summary'] || '';
    const date = paper['Marca temporal'] || paper['Timestamp'] || paper['Date Submitted'] || 
                paper['timestamp'] || paper['Submit Time'] || '';
    const link = paper['PDF Upload'] || paper['Link'] || paper['Paper Link'] || paper['URL'] || 
                paper['Download Link'] || paper['PDF Link'] || '';
    
    let dateDisplay = '';
    if (date && date.trim()) {
      try {
        let dateObj;
        const trimmedDate = date.trim();
        // Handle Spanish date format: DD/MM/YYYY HH:MM:SS
        if (trimmedDate.includes('/') && trimmedDate.match(/\d{2}\/\d{2}\/\d{4}/)) {
          const parts = trimmedDate.split(' ');
          const datePart = parts[0]; 
          const timePart = parts[1] || ''; 
          const [day, month, year] = datePart.split('/');
          const isoDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}${timePart ? 'T' + timePart : ''}`;
          dateObj = new Date(isoDate);
        } else {
          dateObj = new Date(trimmedDate);
        }
        
        if (isNaN(dateObj.getTime())) {
          dateDisplay = trimmedDate; 
        } else {
          dateDisplay = dateObj.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          });
        }
      } catch (e) {
        console.warn('Date parsing error for:', date, e);
        dateDisplay = date.trim();
      }
    }

    // Title Link Logic
    const titleHtml = link ? 
      `<a href="${link}" target="_blank" rel="noopener noreferrer">${escapeHtml(title)}</a>` : 
      escapeHtml(title);

    // Download Button Icon (SVG)
    const downloadIcon = `
      <svg role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-labelledby="downloadIconTitle" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none">
        <title id="downloadIconTitle">Download</title>
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
      </svg>
    `;

    paperItem.innerHTML = `
      <div class="paper-header">
        <div class="paper-title">${titleHtml}</div>
        ${dateDisplay ? `<div class="paper-date">Submitted: ${dateDisplay}</div>` : ''}
      </div>
      
      <div class="paper-authors">
        <div class="author-block">
          <span class="author-name">${escapeHtml(author)}</span>
          ${affiliation ? `<span class="author-affiliation"> — ${escapeHtml(affiliation)}</span>` : ''}
        </div>
      </div>
      
      ${abstract ? `<div class="paper-abstract">${escapeHtml(abstract)}</div>` : ''}
      
      ${link ? `
      <div class="paper-actions">
        <a href="${link}" class="button-download" target="_blank" rel="noopener noreferrer">
          ${downloadIcon}
          Download Paper
        </a>
      </div>` : ''}
    `;

    papersList.appendChild(paperItem);
      } catch (error) {
        console.error('Error processing paper:', error, paper);
        // Continue with next paper even if one fails
      }
  });

  container.innerHTML = '';
  container.appendChild(papersList);
  } catch (error) {
    console.error('Error in displayPapers:', error);
    container.innerHTML = `
      <div class="papers-error">
        <p>Error displaying working papers: ${error.message}</p>
        <p>Please check the browser console for more details.</p>
      </div>
    `;
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

