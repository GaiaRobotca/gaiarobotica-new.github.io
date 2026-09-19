(() => {
  const target = document.getElementById('redirect-target');
  if (target) location.replace(target.getAttribute('href') + location.search + location.hash);
})();
