(() => {
  const btn = document.querySelector(".back-to-top");  // Get the button element
  if (!btn) return; // Exit if button is not found

  const SHOW_AFTER_PX = 10; // Show button after scrolling down

  // Function to toggle visibility
  const setVisibility = () => { 
    btn.classList.toggle("is-visible", window.scrollY > SHOW_AFTER_PX); // CSS uses .is-visible to show/hide
  };

  setVisibility(); // Initial run - in case page is loaded scrolled down
  window.addEventListener("scroll", setVisibility, { passive: true });  // Run on scroll, passive for performance

  // Scroll to top on click
  btn.addEventListener("click", (e) => {
    e.preventDefault(); // Prevent href default action (the fallback)
    window.scrollTo({ top: 0, behavior: "smooth" }); // Scroll to top smoothly 
  });

  // Bootstrap tooltip (if Bootstrap JS is present)
  if (window.bootstrap?.Tooltip) {
    new window.bootstrap.Tooltip(btn);
  }
})();
