/**
 * Hides the breadcrumb bar when the user scrolls down, shows it when they scroll up.
 * Bar stays visible when the page is near the top (within TOP_ZONE_PX).
 */
(() => {
  const bar = document.getElementById("breadcrumb-bar");
  if (!bar) return;

  const HIDDEN_CLASS = "-translate-y-full";
  const SCROLL_THRESHOLD_PX = 10;
  const TOP_ZONE_PX = 80;
  let lastScrollY = window.scrollY;
  let ticking = false;

  const update = () => {
    const scrollY = window.scrollY;
    const atTop = scrollY <= TOP_ZONE_PX;
    const scrolledDown = scrollY > lastScrollY && scrollY > SCROLL_THRESHOLD_PX;

    if (atTop) {
      bar.classList.remove(HIDDEN_CLASS);
    } else if (scrolledDown) {
      bar.classList.add(HIDDEN_CLASS);
    } else {
      bar.classList.remove(HIDDEN_CLASS);
    }

    lastScrollY = scrollY;
    ticking = false;
  };

  const onScroll = () => {
    if (!ticking) {
      requestAnimationFrame(update);
      ticking = true;
    }
  };

  window.addEventListener("scroll", onScroll, { passive: true });
})();
