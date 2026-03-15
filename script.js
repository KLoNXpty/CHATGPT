const toggle = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.nav-links');
const year = document.getElementById('year');

if (toggle && navLinks) {
  toggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });

  document.addEventListener('click', (event) => {
    if (!navLinks.contains(event.target) && !toggle.contains(event.target)) {
      navLinks.classList.remove('open');
    }
  });

  navLinks.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => navLinks.classList.remove('open'));
  });
}

if (year) {
  year.textContent = new Date().getFullYear();
}
