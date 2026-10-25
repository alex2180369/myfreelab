// Runs the LIVE page of a site in jsdom, clicks the CTA, fills the form and submits it.
// fetch is stubbed, so no data is written anywhere.
// Usage: node jsdom_form_test.js <url> <cta-selector> <form-id> <status-id> '<json fields>'
const { JSDOM, VirtualConsole } = require(process.env.HOME + "/tools/node_modules/jsdom");

const [url, ctaSel, formId, statusId, fieldsJson] = process.argv.slice(2);
const fields = JSON.parse(fieldsJson);
const calls = [];
const errors = [];

const vc = new VirtualConsole();
vc.on("jsdomError", (e) => errors.push(String(e.message || e)));
vc.on("error", (e) => errors.push(String(e)));

JSDOM.fromURL(url, {
  runScripts: "dangerously",
  resources: "usable",
  pretendToBeVisual: true,
  virtualConsole: vc,
  beforeParse(window) {
    window.fetch = (u, opts) => {
      calls.push({ url: String(u).slice(0, 60) + "...", body: opts && opts.body });
      return Promise.resolve({ ok: true, status: 200 });
    };
  },
}).then((dom) => new Promise((resolve) => {
  const { window } = dom;
  window.addEventListener("load", async () => {
    const d = window.document;
    const out = {};
    const cta = d.querySelector(ctaSel);
    out.ctaFound = !!cta;
    const modal = d.getElementById("contact-modal");
    out.modalHiddenBefore = modal ? modal.hidden : "no modal";
    if (cta) cta.dispatchEvent(new window.MouseEvent("click", { bubbles: true, cancelable: true }));
    out.modalHiddenAfterClick = modal ? modal.hidden : "no modal";

    const form = d.getElementById(formId);
    out.formFound = !!form;
    if (form) {
      for (const [k, v] of Object.entries(fields)) {
        if (form.elements[k]) form.elements[k].value = v;
      }
      form.dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
      await new Promise((r) => setTimeout(r, 400));
      const st = d.getElementById(statusId);
      out.statusText = st ? st.textContent : "no status element";
      out.statusClass = st ? st.className : "";
    }
    out.fetchCalls = calls.length;
    out.fetchBody = calls[0] ? calls[0].body : null;
    out.scriptErrors = errors;
    console.log(JSON.stringify(out, null, 2));
    window.close();
    resolve();
  });
}));
