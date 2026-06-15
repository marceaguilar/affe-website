// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const navMenu = document.querySelector('.nav-menu');
  const navLinks = document.querySelectorAll('.nav-menu a');

  if (mobileMenuToggle && navMenu) {
    // Toggle menu on button click
    mobileMenuToggle.addEventListener('click', function() {
      navMenu.classList.toggle('active');
      mobileMenuToggle.classList.toggle('active');
      // Prevent body scroll when menu is open
      if (navMenu.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
    });

    // Close menu when clicking on a link
    navLinks.forEach(function(link) {
      link.addEventListener('click', function() {
        navMenu.classList.remove('active');
        mobileMenuToggle.classList.remove('active');
        document.body.style.overflow = '';
      });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
      const isClickInsideNav = navMenu.contains(event.target);
      const isClickOnToggle = mobileMenuToggle.contains(event.target);
      
      if (!isClickInsideNav && !isClickOnToggle && navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
        mobileMenuToggle.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  document.querySelectorAll('.announcement-toggle').forEach(function(button) {
    button.addEventListener('click', function() {
      const details = button.previousElementSibling;
      const isExpanded = button.getAttribute('aria-expanded') === 'true';
      const label = button.querySelector('.announcement-toggle-label');

      if (isExpanded) {
        details.hidden = true;
        button.setAttribute('aria-expanded', 'false');
        if (label) label.textContent = 'Read more';
      } else {
        details.hidden = false;
        button.setAttribute('aria-expanded', 'true');
        if (label) label.textContent = 'Show less';
      }
    });
  });

  document.querySelectorAll('.webinar-abstract-toggle').forEach(function(button) {
    button.addEventListener('click', function() {
      const abstract = button.previousElementSibling;
      const isExpanded = button.getAttribute('aria-expanded') === 'true';
      const label = button.querySelector('.webinar-abstract-toggle-label');

      if (isExpanded) {
        abstract.classList.add('is-collapsed');
        button.setAttribute('aria-expanded', 'false');
        if (label) label.textContent = 'Read abstract';
      } else {
        abstract.classList.remove('is-collapsed');
        button.setAttribute('aria-expanded', 'true');
        if (label) label.textContent = 'Show less';
      }
    });
  });
});

