---
layout: default
title: Past Conferences
---

<h1 class="page-title">Past Conferences</h1>

<div class="conferences-container">
  {% if site.data.past_conferences %}
    <ul class="past-conferences-list">
      {% for conference in site.data.past_conferences %}
        <li class="past-conference-item">
          {% if conference.link %}
            <a href="{{ conference.link }}" target="_blank" rel="noopener noreferrer">
              {{ conference.title }} - {{ conference.date }}
            </a>
          {% else %}
            {{ conference.title }} - {{ conference.date }}
          {% endif %}
          {% if conference.location %}
            <span style="color: var(--color-text-light);"> ({{ conference.location }})</span>
          {% endif %}
        </li>
      {% endfor %}
    </ul>
  {% else %}
    <!-- Default example -->
    <ul class="past-conferences-list">
      <li class="past-conference-item">
        <a href="#">2024 WEFIDEV Conference - Example</a>
      </li>
      <li class="past-conference-item">
        <a href="#">2023 WEFIDEV Conference - Example</a>
      </li>
    </ul>
  {% endif %}
</div>

<!-- <div style="margin-top: 2rem; padding: 1rem; background-color: var(--color-parchment); border-radius: 4px;">
  <p><strong>Note:</strong> To add past conferences, create a <code>_data/past_conferences.yml</code> file with the following format:</p>
  <pre><code>- title: "Conference Name"
  date: "March 2024"
  location: "Location"
  link: "https://conference-website.com"
- title: "Another Conference"
  date: "September 2023"
  location: "Another Location"
  link: "https://another-link.com"</code></pre>
</div>
 -->
