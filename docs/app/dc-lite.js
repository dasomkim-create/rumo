/* dc-lite — a small runtime that renders RUMO's .dc.html design files with React.
   Supports: {{holes}}, <sc-if>, <sc-for>, <dc-import>, <helmet> styles, DCLogic classes,
   events (onClick …), and links between screens (href="X.dc.html"). */
(function () {
  const h = React.createElement;
  const BLOB = (window.DC_BLOB_BASE || '../blobs/');
  const SCREENS = (window.DC_SCREEN_BASE || 'screens/');
  const FONT_ID = 'e716050c98566c9e615f5e9d7d2cdbd6';
  const defs = {};       // name -> {nodes, Logic, preview}
  const loading = {};
  const styled = new Set();

  class DCLogic {
    constructor(props) { this.props = props || {}; this.state = {}; }
    setState(patch, cb) {
      const next = typeof patch === 'function' ? patch(this.state, this.props) : patch;
      this.state = Object.assign({}, this.state, next);
      if (this.__host) this.__host.forceUpdate(cb); else if (cb) cb();
    }
    forceUpdate(cb) { if (this.__host) this.__host.forceUpdate(cb); }
    renderVals() { return {}; }
  }
  window.DCLogic = DCLogic;

  function rewriteBlobs(t) {
    return t.replace(/\/_blob\/([0-9a-f]{32})/g, (m, id) => BLOB + id + (id === FONT_ID ? '.woff2' : '.svg'));
  }

  function load(name) {
    if (defs[name]) return Promise.resolve(defs[name]);
    if (loading[name]) return loading[name];
    loading[name] = fetch(SCREENS + name + '.dc.html').then((r) => {
      if (!r.ok) throw new Error('missing ' + name);
      return r.text();
    }).then((txt) => {
      txt = rewriteBlobs(txt);
      const doc = new DOMParser().parseFromString(txt, 'text/html');
      const xdc = doc.querySelector('x-dc');
      const helmet = xdc.querySelector('helmet');
      if (helmet && !styled.has(name)) {
        styled.add(name);
        helmet.querySelectorAll('style').forEach((s) => {
          const el = document.createElement('style'); el.dataset.dc = name; el.textContent = s.textContent; document.head.appendChild(el);
        });
      }
      const nodes = Array.from(xdc.childNodes).filter((n) => !(n.nodeType === 1 && n.tagName.toLowerCase() === 'helmet'));
      const sc = doc.querySelector('script[data-dc-script]');
      let Logic = DCLogic, preview = null;
      if (sc) {
        try { const p = JSON.parse(sc.getAttribute('data-props') || '{}'); preview = p.$preview || null; } catch (e) {}
        Logic = new Function('DCLogic', sc.textContent + '\n;return Component;')(DCLogic);
      }
      const def = { nodes, Logic, preview };
      defs[name] = def;
      const deps = new Set();
      xdc.querySelectorAll('dc-import').forEach((d) => deps.add(d.getAttribute('name')));
      return Promise.all(Array.from(deps).map(load)).then(() => def);
    });
    return loading[name];
  }

  // ---------- holes
  function lookup(path, scope) {
    path = path.trim();
    if (path === 'true') return true;
    if (path === 'false') return false;
    if (path === 'null') return null;
    if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
    if (/^(['"]).*\1$/.test(path)) return path.slice(1, -1);
    let cur = scope;
    for (const k of path.split('.')) { if (cur == null) return undefined; cur = cur[k]; }
    return cur;
  }
  const WHOLE = /^\s*\{\{([^}]+)\}\}\s*$/;
  function interp(str, scope) {
    const m = str.match(WHOLE);
    if (m) return lookup(m[1], scope);
    return str.replace(/\{\{([^}]+)\}\}/g, (_, p) => { const v = lookup(p, scope); return v == null ? '' : String(v); });
  }

  // ---------- attributes
  const EVENTS = { onclick: 'onClick', onmouseenter: 'onMouseEnter', onmouseleave: 'onMouseLeave', oninput: 'onInput', onfocus: 'onFocus', onblur: 'onBlur', onmousedown: 'onMouseDown', onmouseup: 'onMouseUp', onchange: 'onChange', onkeydown: 'onKeyDown', onkeyup: 'onKeyUp', onsubmit: 'onSubmit', onpointerdown: 'onPointerDown' };
  const RENAME = { class: 'className', for: 'htmlFor', tabindex: 'tabIndex', readonly: 'readOnly', maxlength: 'maxLength', autocomplete: 'autoComplete', autofocus: 'autoFocus', colspan: 'colSpan', rowspan: 'rowSpan', crossorigin: 'crossOrigin', srcset: 'srcSet', 'xlink:href': 'xlinkHref', 'xml:space': 'xmlSpace' };
  const camel = (s) => s.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
  function styleObj(str) {
    const o = {};
    if (!str) return o;
    let depth = 0, buf = '', parts = [];
    for (const ch of String(str)) { if (ch === '(') depth++; if (ch === ')') depth--; if (ch === ';' && depth === 0) { parts.push(buf); buf = ''; } else buf += ch; }
    parts.push(buf);
    for (const decl of parts) {
      const i = decl.indexOf(':'); if (i < 0) continue;
      let k = decl.slice(0, i).trim(); const v = decl.slice(i + 1).trim();
      if (!k) continue;
      if (!k.startsWith('--')) { if (k.startsWith('-webkit-')) { const c = camel(k.slice(8)); k = 'Webkit' + c.charAt(0).toUpperCase() + c.slice(1); } else k = camel(k); }
      o[k] = v;
    }
    return o;
  }

  // ---------- render template nodes
  function renderNodes(nodes, scope, keyBase) {
    const out = [];
    nodes.forEach((n, i) => {
      const r = renderNode(n, scope, keyBase + '.' + i);
      if (r === null || r === undefined || r === false) return;
      if (Array.isArray(r)) r.forEach((x) => out.push(x)); else out.push(r);
    });
    return out;
  }
  function renderNode(n, scope, key) {
    if (n.nodeType === 3) {
      const t = n.nodeValue;
      if (!t.trim() && /\n/.test(t)) return null;
      const v = interp(t, scope);
      return v == null ? '' : (typeof v === 'object' ? '' : v);
    }
    if (n.nodeType !== 1) return null;
    const tag = n.tagName.toLowerCase();
    if (tag === 'sc-if') {
      const v = interp(n.getAttribute('value') || '', scope);
      return v ? h(React.Fragment, { key }, renderNodes(Array.from(n.childNodes), scope, key)) : null;
    }
    if (tag === 'sc-for') {
      const list = interp(n.getAttribute('list') || '', scope) || [];
      const as = n.getAttribute('as') || 'item';
      return (Array.isArray(list) ? list : []).map((item, idx) => {
        const s = Object.create(scope); s[as] = item; s.$index = idx;
        return h(React.Fragment, { key: key + ':' + idx }, renderNodes(Array.from(n.childNodes), s, key + ':' + idx));
      });
    }
    if (tag === 'dc-import') {
      const name = n.getAttribute('name');
      const props = { key };
      for (const a of Array.from(n.attributes)) {
        if (a.name === 'name' || a.name.startsWith('hint-')) continue;
        props[camel(a.name)] = interp(a.value, scope);
      }
      return h(DC, Object.assign(props, { __name: name }));
    }
    const props = { key };
    for (const a of Array.from(n.attributes)) {
      let k = a.name; let v = interp(a.value, scope);
      if (EVENTS[k]) { if (typeof v === 'function') props[EVENTS[k]] = v; continue; }
      if (k === 'style') { props.style = styleObj(v); continue; }
      if (RENAME[k]) k = RENAME[k];
      else if (!k.startsWith('data-') && !k.startsWith('aria-') && k.includes('-')) k = camel(k);
      if (v === undefined || v === null) continue;
      props[k] = v;
    }
    if ((tag === 'input' || tag === 'textarea') && 'value' in props && !props.onChange) props.onChange = props.onInput || (() => {});
    const kids = renderNodes(Array.from(n.childNodes), scope, key);
    return h(tag, props, ...(kids.length ? kids : []));
  }

  // ---------- component host
  class DC extends React.Component {
    constructor(p) {
      super(p);
      const name = p.__name;
      this.def = defs[name];
      const props = Object.assign({}, p); delete props.__name; delete props.key;
      this.inst = new this.def.Logic(props);
      if (!this.inst.state) this.inst.state = {};
      this.inst.__host = this;
    }
    componentDidMount() { if (this.inst.componentDidMount) this.inst.componentDidMount(); }
    componentDidUpdate(pp) { if (this.inst.componentDidUpdate) this.inst.componentDidUpdate(pp); }
    componentWillUnmount() { this.inst.__host = null; if (this.inst.componentWillUnmount) this.inst.componentWillUnmount(); }
    render() {
      const props = Object.assign({}, this.props); delete props.__name;
      this.inst.props = props;
      let vals = {};
      try { vals = this.inst.renderVals() || {}; } catch (e) { console.error(this.props.__name, e); }
      return h(React.Fragment, null, renderNodes(this.def.nodes, vals, 'r'));
    }
  }

  window.DCLite = { load, DC, defs, preview: (n) => (defs[n] && defs[n].preview) || null };
})();
