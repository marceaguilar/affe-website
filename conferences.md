---
layout: default
title: Conference Postings
---

<h1 class="page-title">Conference Postings</h1>

<div class="conferences-container">
  
  {% if site.data.conferences %}
    {% for conference in site.data.conferences %}
      <div class="conference-card">
        <div class="conference-title">{{ conference.title }}</div>
        <div class="conference-date">{{ conference.date }}</div>
        <div class="conference-description">{{ conference.description | markdownify }}</div>
        {% if conference.link %}
          <a href="{{ conference.link }}" target="_blank" rel="noopener noreferrer" class="conference-link">
            {% if conference.link_text %}{{ conference.link_text }}{% else %}Learn More{% endif %}
          </a>
        {% endif %}
        {% if conference.deadline %}
          <p style="margin-top: 1rem; color: var(--color-bark);"><strong>Deadline:</strong> {{ conference.deadline }}</p>
        {% endif %}
      </div>
    {% endfor %}
  {% else %}
    <!-- Default example -->
    <div class="conference-card">
      <div class="conference-title">Upcoming Conference</div>
      <div class="conference-date">TBD</div>
      <div class="conference-description">
        <p>Details about upcoming conferences will be posted here. Check back soon for updates.</p>
      </div>
    </div>
  {% endif %}

</div>

<div style="margin-top: 2rem; padding: 1rem; background-color: var(--color-parchment); border-radius: 4px;">
  <p><strong>Note:</strong> To add conference postings, create a <code>_data/conferences.yml</code> file with the following format:</p>
  <pre><code>- title: "Conference Name"
  date: "March 15-17, 2025"
  description: "Conference description in markdown"
  link: "https://conference-url.com"
  link_text: "Register Here"
  deadline: "Submission deadline: February 1, 2025"</code></pre>
</div>

