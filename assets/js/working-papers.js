// Static working papers data
const staticPapers = [
  {
    'Title': 'Artificial Intelligence and the Restructuring of the Organizational Architecture',
    'Authors': 'Jasmijn C. Bol (Tulane University), Dennis Campbell (Harvard University), Jake Krupa (Tulane University), Wenxin Wang (Harvard University)',
    'Link': '/assets/pdf/BCKW.pdf'
  },
  {
    'Title': 'Paid Tax Preparers and Social Benefit Take-up: Evidence from a Field Experiment',
    'Authors': 'Andrew Belnap (University of Texas at Austin), Anthony Welsch (University of Chicago), Jeffrey Gramlich (Washington State University), Braden Williams (University of Texas at Austin)',
    'Link': '/assets/pdf/BGWW.pdf'
  },
  {
    'Title': 'Pills, Powders, and Proof',
    'Authors': 'Anna Costello (University of Chicago Booth), Christian Friedrich (University of Mannheim), Gerrit von Zedlitz (University of Mannheim)',
    'Link': '/assets/pdf/CostelloFriedrichvonZedlitz.pdf'
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
    paperItem.className = 'paper-item';
    
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
        // Match DD/MM/YYYY pattern (with optional leading/trailing spaces)
        if (trimmedDate.includes('/') && trimmedDate.match(/\d{2}\/\d{2}\/\d{4}/)) {
          const parts = trimmedDate.split(' ');
          const datePart = parts[0]; // "22/11/2025"
          const timePart = parts[1] || ''; // "1:40:20"
          const [day, month, year] = datePart.split('/');
          // Create date in ISO format (YYYY-MM-DD) which is reliably parsed
          const isoDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}${timePart ? 'T' + timePart : ''}`;
          dateObj = new Date(isoDate);
        } else {
          // Try standard Date parsing for other formats
          dateObj = new Date(trimmedDate);
        }
        
        // Check if date is valid
        if (isNaN(dateObj.getTime())) {
          dateDisplay = trimmedDate; // Fallback to original string
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

    const titleHtml = link ? 
      `<a href="${link}" target="_blank" rel="noopener noreferrer">${escapeHtml(title)}</a>` : 
      escapeHtml(title);

    paperItem.innerHTML = `
      <div class="paper-title">${titleHtml}</div>
      <div class="paper-author">${escapeHtml(author)}${affiliation ? `, ${escapeHtml(affiliation)}` : ''}</div>
      ${dateDisplay ? `<div class="paper-date">Submitted: ${dateDisplay}</div>` : ''}
      ${abstract ? `<div class="paper-abstract">${escapeHtml(abstract)}</div>` : ''}
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

