---
layout: default
title: Announcements
---

<h1 class="page-title">Announcements</h1>

<div class="announcements-container">
  <div class="timeline">
    
    <!-- Example announcement - you can add more in _data/announcements.yml -->
    {% if site.data.announcements %}
      {% for announcement in site.data.announcements %}
        <div class="timeline-item">
          <div class="announcement-card">
            <div class="announcement-date">{{ announcement.date }}</div>
            <div class="announcement-title">{{ announcement.title }}</div>
            <div class="announcement-content">{{ announcement.content | markdownify }}</div>
          </div>
        </div>
      {% endfor %}
    {% else %}
      <!-- Default example announcement -->
      <div class="timeline-item">
        <div class="announcement-card">
          <div class="announcement-date">{{ "now" | date: "%B %d, %Y" }}</div>
          <div class="announcement-title">Welcome to WEFIDEV</div>
          <div class="announcement-content">
            <p>We're excited to launch our new website. Check back regularly for updates on upcoming webinars, conference postings, and working papers.</p>
          </div>
        </div>
      </div>
    {% endif %}

  </div>
</div>

<!-- <div style="margin-top: 2rem; padding: 1rem; background-color: var(--color-parchment); border-radius: 4px;">
  <p><strong>Note:</strong> To add announcements, create a <code>_data/announcements.yml</code> file with the following format:</p>
  <pre><code>- date: "January 15, 2025"
  title: "Announcement Title"
  content: "Announcement content in markdown format"
- date: "January 20, 2025"
  title: "Another Announcement"
  content: "More content here"</code></pre>
</div> -->

