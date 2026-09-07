(function () {
  var JA = document.documentElement.lang === 'ja';
  var root = document.documentElement;
  function isDark() {
    var t = root.getAttribute('data-theme');
    if (t) return t === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  // ---- menu
  var mb = document.querySelector('[data-menu]');
  var nav = document.querySelector('.topnav');
  if (mb && nav) mb.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    mb.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // ---- collapsible docs sidebar on narrow screens
  var st = document.querySelector('[data-side-toggle]');
  if (st) st.addEventListener('click', function () {
    var side = st.closest('.side'); var open = side.classList.toggle('open');
    st.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // ---- collapsible side columns (docs); state persisted per browser
  document.querySelectorAll('[data-collapse]').forEach(function (b) {
    b.addEventListener('click', function () {
      var which = b.getAttribute('data-collapse');
      if (which === 'toc') {
        var open = root.classList.contains('toc-open');
        root.classList.toggle('toc-open', !open); root.classList.toggle('toc-closed', open);
        try { localStorage.setItem('zkfmi-toc', open ? 'closed' : 'open'); } catch (e) {}
      } else {
        var closed = root.classList.toggle('side-closed');
        try { localStorage.setItem('zkfmi-side', closed ? 'closed' : 'open'); } catch (e) {}
      }
      setTimeout(fitDiagrams, 200);
    });
  });

  // ---- theme toggle (persisted per browser; system preference otherwise)
  var tb = document.querySelector('[data-theme-toggle]');
  if (tb) tb.addEventListener('click', function () {
    var next = isDark() ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('zkfmi-theme', next); } catch (e) {}
    renderMermaid(true);
  });

  // ---- mermaid, themed to the palette in use
  var mermaidSources = null;
  function mermaidVars() {
    return isDark() ? {
      background: '#10161e', primaryColor: '#171f2a', primaryTextColor: '#e8eef4', primaryBorderColor: '#3a4a5e',
      lineColor: '#8899ad', secondaryColor: '#1a2430', tertiaryColor: '#121a24', fontFamily: '"JetBrains Mono", ui-monospace, Menlo, monospace', fontSize: '13px',
      clusterBkg: '#0f151d', clusterBorder: '#2a3644', edgeLabelBackground: '#10161e', noteBkgColor: '#1a2430', noteTextColor: '#e8eef4', noteBorderColor: '#3a4a5e',
      actorBkg: '#171f2a', actorBorder: '#3a4a5e', actorTextColor: '#e8eef4', signalColor: '#aab7c5', signalTextColor: '#e8eef4', labelBoxBkgColor: '#171f2a', labelTextColor: '#e8eef4', sequenceNumberColor: '#06110e'
    } : {
      background: '#f3f6f9', primaryColor: '#ffffff', primaryTextColor: '#0e1622', primaryBorderColor: '#b9c5d3',
      lineColor: '#4f6076', secondaryColor: '#e9eef4', tertiaryColor: '#f3f6f9', fontFamily: '"JetBrains Mono", ui-monospace, Menlo, monospace', fontSize: '13px',
      clusterBkg: '#eef2f6', clusterBorder: '#cbd5df', edgeLabelBackground: '#f3f6f9', noteBkgColor: '#fff7e8', noteTextColor: '#0e1622', noteBorderColor: '#e0c9a0',
      actorBkg: '#ffffff', actorBorder: '#b9c5d3', actorTextColor: '#0e1622', signalColor: '#3b4959', signalTextColor: '#0e1622', labelBoxBkgColor: '#ffffff', labelTextColor: '#0e1622', sequenceNumberColor: '#ffffff'
    };
  }
  function fitDiagrams() {
    document.querySelectorAll('pre.mermaid svg').forEach(function (s) {
      var vb = (s.getAttribute('viewBox') || '').split(/\s+/).map(Number);
      var w = vb[2] || 0, cw = s.parentElement.clientWidth - 32;
      if (w > cw * 1.3) { s.style.maxWidth = 'none'; s.style.width = Math.round(Math.max(cw, w * 0.8)) + 'px'; }
      else { s.style.maxWidth = ''; s.style.width = '100%'; }
    });
  }
  function renderMermaid(rerender) {
    if (!window.mermaid) return;
    var blocks = document.querySelectorAll('pre.mermaid');
    if (!blocks.length) return;
    if (!mermaidSources) mermaidSources = Array.prototype.map.call(blocks, function (b) { return b.textContent; });
    if (rerender) blocks.forEach(function (b, i) { b.removeAttribute('data-processed'); b.innerHTML = ''; b.textContent = mermaidSources[i]; });
    mermaid.initialize({ startOnLoad: false, theme: 'base', securityLevel: 'loose', themeVariables: mermaidVars(), flowchart: { htmlLabels: true, curve: 'basis' } });
    mermaid.run({ nodes: blocks }).then(fitDiagrams).catch(function (e) { console.warn('mermaid', e); });
  }
  renderMermaid(false);
  window.addEventListener('resize', fitDiagrams);

  // ---- heading anchors + copy buttons
  document.querySelectorAll('.doc h2[id]').forEach(function (h) {
    var a = document.createElement('a'); a.className = 'anchor'; a.href = '#' + h.id; a.textContent = '#'; a.setAttribute('aria-label', JA ? 'この節へのリンク' : 'Link to this section'); h.appendChild(a);
  });
  document.querySelectorAll('pre:not(.mermaid)').forEach(function (pre) {
    var b = document.createElement('button'); b.className = 'copy'; b.type = 'button'; b.textContent = JA ? 'コピー' : 'copy';
    b.addEventListener('click', function () {
      var code = pre.querySelector('code'); var text = (code || pre).innerText;
      navigator.clipboard.writeText(text).then(function () { b.textContent = JA ? 'コピーした' : 'copied'; setTimeout(function () { b.textContent = JA ? 'コピー' : 'copy'; }, 1200); });
    });
    pre.appendChild(b);
  });

  // ---- table of contents scroll spy
  var tocLinks = document.querySelectorAll('.toc a[href^="#"]');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var current = null;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) current = en.target.id; });
      if (current && map[current]) { tocLinks.forEach(function (a) { a.classList.remove('on'); }); map[current].classList.add('on'); }
    }, { rootMargin: '-70px 0px -70% 0px', threshold: 0 });
    Object.keys(map).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }

  // ---- search
  var modal = document.querySelector('[data-search-modal]');
  var input = document.querySelector('[data-search-input]');
  var results = document.querySelector('[data-search-results]');
  var index = null, sel = -1;
  var rel = (document.querySelector('link[rel=stylesheet][href$="style.css"]') || {}).getAttribute ? document.querySelector('link[rel=stylesheet][href$="style.css"]').getAttribute('href').replace('style.css', '') : '';
  function openSearch() {
    if (!modal) return;
    modal.hidden = false; input.value = ''; results.innerHTML = ''; sel = -1; input.focus();
    if (!index) fetch(document.body.getAttribute('data-search') || (rel + 'search.json')).then(function (r) { return r.json(); }).then(function (j) { index = j; });
  }
  function closeSearch() { if (modal) modal.hidden = true; }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function mark(s, terms) {
    var out = esc(s);
    terms.forEach(function (t) { if (t.length > 1) out = out.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); });
    return out;
  }
  function score(e, terms) {
    var t = e.t.toLowerCase(), h = e.h.toLowerCase(), x = e.x.toLowerCase(), s = 0;
    for (var i = 0; i < terms.length; i++) {
      var q = terms[i]; if (!q) continue;
      if (t.indexOf(q) >= 0) s += 6; if (h.indexOf(q) >= 0) s += 4; if (x.indexOf(q) >= 0) s += 1;
      if (t.indexOf(q) < 0 && h.indexOf(q) < 0 && x.indexOf(q) < 0) return 0;
    }
    return s;
  }
  function runSearch() {
    if (!index) return;
    var q = input.value.trim().toLowerCase(); var terms = q.split(/\s+/).filter(Boolean);
    results.innerHTML = ''; sel = -1;
    if (!terms.length) return;
    var hits = index.map(function (e) { return { e: e, s: score(e, terms) }; }).filter(function (r) { return r.s > 0; }).sort(function (a, b) { return b.s - a.s; }).slice(0, 12);
    hits.forEach(function (r) {
      var li = document.createElement('li');
      var snippet = r.e.x; var pos = snippet.toLowerCase().indexOf(terms[0]);
      if (pos > 80) snippet = '…' + snippet.slice(pos - 60);
      li.innerHTML = '<a href="' + rel + r.e.u + '"><span class="st">' + mark(r.e.t, terms) + (r.e.h ? '<small>› ' + mark(r.e.h, terms) + '</small>' : '') + '</span><span class="sx">' + mark(snippet.slice(0, 160), terms) + '</span></a>';
      results.appendChild(li);
    });
    if (!hits.length) results.innerHTML = '<li><span class="sx" style="padding:.6rem 1.1rem;display:block">' + (JA ? '該当なし。' : 'No matches.') + '</span></li>';
  }
  if (modal) {
    document.querySelectorAll('[data-search-open]').forEach(function (b) { b.addEventListener('click', openSearch); });
    modal.addEventListener('click', function (e) { if (e.target === modal) closeSearch(); });
    input.addEventListener('input', runSearch);
    input.addEventListener('keydown', function (e) {
      var items = results.querySelectorAll('li');
      if (e.key === 'ArrowDown') { sel = Math.min(sel + 1, items.length - 1); e.preventDefault(); }
      else if (e.key === 'ArrowUp') { sel = Math.max(sel - 1, 0); e.preventDefault(); }
      else if (e.key === 'Enter') { var a = (items[sel] || items[0]); if (a) { var l = a.querySelector('a'); if (l) location.href = l.href; } return; }
      else return;
      items.forEach(function (li, i) { li.classList.toggle('on', i === sel); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeSearch();
      if (e.key === '/' && modal.hidden && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); openSearch(); }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); openSearch(); }
    });
  }
})();
