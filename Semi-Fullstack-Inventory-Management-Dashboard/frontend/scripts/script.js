
// set active link
function setActiveLink() {
    // all links
    const links = document.querySelectorAll('.sidepanel a');
    
    // current page path
    const currentPage = window.location.pathname.split('/').pop();
  
    // remove active
    links.forEach(link => {
      link.classList.remove('active');
    });
  
    // add active
    const activeLink = document.querySelector(`#${currentPage}-link`);
    if (activeLink) {
      activeLink.classList.add('active');
    }
  }
  
  // main entry
  window.addEventListener('DOMContentLoaded', setActiveLink);
  