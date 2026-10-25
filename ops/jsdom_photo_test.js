// Runs the LIVE photographer site (React bundle) in jsdom, fills the first form and submits it.
// jsdom cannot run <script type="module">, so the bundle is evaluated as a classic script.
// fetch is stubbed: nothing is written to the table.
const { JSDOM, VirtualConsole } = require(process.env.HOME + "/tools/node_modules/jsdom");

const SITE = process.argv[2] || "https://photo.myfreelab.ru/";
const calls = [];
const errors = [];

async function main() {
  const html = await (await fetch(SITE, { cache: "no-store" })).text();
  const m = html.match(/<script[^>]*type="module"[^>]*src="([^"]+)"/);
  if (!m) throw new Error("module script not found");
  const bundleUrl = new URL(m[1], SITE).href;
  const bundle = await (await fetch(bundleUrl)).text();

  const vc = new VirtualConsole();
  vc.on("jsdomError", (e) => errors.push(String(e.message || e).slice(0, 200)));
  vc.on("error", (e) => errors.push(String(e).slice(0, 200)));

  const dom = new JSDOM(html.replace(/<script[^>]*type="module"[^>]*><\/script>/, ""), {
    url: SITE,
    runScripts: "outside-only",
    pretendToBeVisual: true,
    virtualConsole: vc,
  });
  const { window } = dom;
  window.fetch = (u, opts) => {
    calls.push({ url: String(u), body: opts && opts.body });
    return Promise.resolve({ ok: true, status: 200, json: async () => ({ ok: true }) });
  };
  window.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
  window.matchMedia = window.matchMedia || (() => ({ matches: false, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} }));
  window.scrollTo = () => {};
  window.eval(bundle);
  await new Promise((r) => setTimeout(r, 1500));

  const d = window.document;
  const out = { bundle: m[1], rootChildren: d.getElementById("root").children.length };
  const form = d.querySelector("form");
  out.formFound = !!form;
  if (form) {
    const setNative = (el, value) => {
      const proto = el.tagName === "SELECT" ? window.HTMLSelectElement.prototype
        : el.tagName === "TEXTAREA" ? window.HTMLTextAreaElement.prototype
        : window.HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, "value").set.call(el, value);
      el.dispatchEvent(new window.Event("input", { bubbles: true }));
      el.dispatchEvent(new window.Event("change", { bubbles: true }));
    };
    out.fields = [];
    form.querySelectorAll("input, textarea, select").forEach((el) => {
      if (["hidden", "submit", "checkbox"].includes(el.type)) return;
      // Fields named company / website are the spam traps: a real visitor never fills them.
      if (/^(company|website)$/i.test(el.name || "")) return;
      out.fields.push(el.name || el.id || el.type);
      if (el.tagName === "SELECT") {
        if (el.options.length) setNative(el, el.options[el.options.length - 1].value);
      } else if (/contact|phone|tel/i.test(el.name || el.type)) setNative(el, "test-check");
      else if (el.tagName === "TEXTAREA") setNative(el, "Проверка эмулятора");
      else setNative(el, "ТЕСТ Лютик");
    });
    form.querySelectorAll("input[type=checkbox]").forEach((c) => {
      c.checked = true;
      c.dispatchEvent(new window.Event("change", { bubbles: true }));
    });
    form.dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
    await new Promise((r) => setTimeout(r, 1000));
    const msg = d.querySelector("[role=status], [role=alert], .success, [class*=status], [class*=success]");
    out.message = msg ? msg.textContent.trim().slice(0, 140) : null;
  }
  out.fetchCalls = calls.map((c) => ({ url: c.url.slice(0, 75) + "...", body: c.body && c.body.slice(0, 300) }));
  out.errors = errors.slice(0, 5);
  console.log(JSON.stringify(out, null, 2));
  window.close();
}
main().catch((e) => { console.log("FAILED:", e.message); });
