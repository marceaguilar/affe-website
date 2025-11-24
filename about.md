---
layout: default
title: About
---

<h1 class="page-title">About WEFIDEV</h1>

<div class="about-container">
  <div class="about-section">
    <h2>Our Mission</h2>
    <p>
      We launched WEFIDEV to support researchers in sharing their work and fostering productive discussions 
      in finance and development. We look forward to continuing to build this community and provide a forum 
      for productive discussion.
    </p>
  </div>

  <div class="about-section">
    <h2>Organizing Committee</h2>
    
    {% if site.data.team %}
      {% for member in site.data.team %}
        <div class="team-member">
          <div class="team-member-name">{{ member.name }}</div>
          <div class="team-member-role">{{ member.role }}</div>
          {% if member.institution %}
            <div class="team-member-institution">{{ member.institution }}</div>
          {% endif %}
        </div>
      {% endfor %}
    {% else %}
      <!-- Default example -->
      <div class="team-member">
        <div class="team-member-name">Organizing Committee</div>
        <div class="team-member-role">WEFIDEV Team</div>
        <div class="team-member-institution">To be updated</div>
      </div>
    {% endif %}
    
  </div>

  <div class="about-section">
    <h2>Contact</h2>
    <p>For questions or inquiries, please contact us at: <a href="mailto:info@wefidev.com">info@wefidev.com</a></p>
  </div>
</div>

<!-- <div style="margin-top: 2rem; padding: 1rem; background-color: var(--color-parchment); border-radius: 4px;">
  <p><strong>Note:</strong> To add team members, create a <code>_data/team.yml</code> file with the following format:</p>
  <pre><code>- name: "Name"
  role: "Role/Title"
  institution: "Institution Name"
- name: "Another Name"
  role: "Another Role"
  institution: "Another Institution"</code></pre>
</div> -->

