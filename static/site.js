(function () {
  var b = document.querySelector('[data-menu]');
  var n = document.querySelector('.topnav');
  if (b && n) b.addEventListener('click', function () {
    var open = n.classList.toggle('open');
    b.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  var dark = document.documentElement.getAttribute('data-theme') === 'dark' ||
    (!document.documentElement.getAttribute('data-theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
  if (window.mermaid) {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'base',
      securityLevel: 'loose',
      themeVariables: dark ? {
        background: '#10161e', primaryColor: '#161e28', primaryTextColor: '#e6edf3', primaryBorderColor: '#3a4a5e',
        lineColor: '#7f90a4', secondaryColor: '#1a2430', tertiaryColor: '#121a24', fontFamily: 'ui-monospace, Menlo, monospace', fontSize: '13px',
        clusterBkg: '#0f151d', clusterBorder: '#2a3644', edgeLabelBackground: '#10161e'
      } : {
        background: '#f3f6f9', primaryColor: '#ffffff', primaryTextColor: '#0e1622', primaryBorderColor: '#b9c5d3',
        lineColor: '#4f6076', secondaryColor: '#e9eef4', tertiaryColor: '#f3f6f9', fontFamily: 'ui-monospace, Menlo, monospace', fontSize: '13px',
        clusterBkg: '#eef2f6', clusterBorder: '#cbd5df', edgeLabelBackground: '#f3f6f9'
      }
    });
  }
  // wide diagrams: keep text legible and let the block scroll instead of shrinking
  function fitDiagrams() {
    document.querySelectorAll('pre.mermaid svg').forEach(function (svg) {
      var vb = (svg.getAttribute('viewBox') || '').split(/\s+/);
      var vbw = parseFloat(vb[2]); var box = svg.parentElement.clientWidth - 32;
      if (!vbw || !box) return;
      if (vbw > box * 1.3) { svg.style.maxWidth = 'none'; svg.style.width = Math.round(Math.max(box, vbw * 0.8)) + 'px'; }
    });
  }
  if (window.mermaid && mermaid.run) {
    mermaid.run({ querySelector: 'pre.mermaid' }).then(fitDiagrams).catch(function () {});
  }
  document.querySelectorAll('.doc h2[id]').forEach(function (h) {
    var a = document.createElement('a'); a.className = 'anchor'; a.href = '#' + h.id; a.textContent = '#'; h.appendChild(a);
  });
})();
