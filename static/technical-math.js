document.addEventListener('DOMContentLoaded', () => {
  if (!window.katex) return;
  for (const element of document.querySelectorAll('[data-math]')) {
    try { katex.render(element.dataset.math, element, {displayMode:true,throwOnError:true,trust:false,strict:false}); }
    catch (_) { element.classList.add('math-source'); }
  }
});
