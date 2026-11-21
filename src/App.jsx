import { useEffect, useState } from 'react';
import site from './content/site.json';
import projects from './content/projects.json';

const LANGS = ['ru', 'en'];
const GROUPS = ['leads', 'sales', 'showcase', 'ops'];
const pad = (n) => String(n).padStart(2, '0');
const tg = `https://t.me/${site.contacts.telegram}`;

function initialLang() {
  try {
    const saved = localStorage.getItem('lang');
    if (LANGS.includes(saved)) return saved;
  } catch {
    /* localStorage недоступен — не страшно */
  }
  return navigator.language?.toLowerCase().startsWith('ru') ? 'ru' : 'en';
}

export default function App() {
  const [lang, setLang] = useState(initialLang);
  const [filter, setFilter] = useState('all');
  const [preset, setPreset] = useState('');
  const t = site[lang];

  useEffect(() => {
    document.documentElement.lang = lang;
    document.title =
      lang === 'ru'
        ? 'Алексей Ан — сайты, квизы, калькуляторы и боты для малого бизнеса'
        : 'Alexey An — websites, quizzes, calculators and bots for small business';
    try {
      localStorage.setItem('lang', lang);
    } catch {
      /* ignore */
    }
  }, [lang]);

  // Кнопки «С чего начнём?» и «Обсудить» в пакетах: выбрать группу работ / подставить текст заявки
  const showGroup = (g) => {
    setFilter(g);
    document.getElementById('work')?.scrollIntoView();
  };
  const discuss = (text) => {
    setPreset(text);
    document.getElementById('contact')?.scrollIntoView();
  };

  return (
    <>
      <TopBar t={t} lang={lang} setLang={setLang} />
      <Header t={t} />
      <main>
        <Hero t={t} showGroup={showGroup} />
        <Work t={t} lang={lang} filter={filter} setFilter={setFilter} />
        <Services t={t} discuss={discuss} />
        <Process t={t} />
        <About t={t} />
        <Faq t={t} />
        <Contact t={t} lang={lang} preset={preset} />
      </main>
      <a href="#contact" className="sticky-cta btn btn--accent">{t.cta}</a>
    </>
  );
}

function TopBar({ t, lang, setLang }) {
  return (
    <div className="topbar">
      <div className="wrap topbar__in">
        <span className="topbar__issue">{t.issue}</span>
        <div className="lang" role="group" aria-label={t.langLabel}>
          {LANGS.map((l) => (
            <button
              key={l}
              type="button"
              aria-pressed={lang === l}
              className={lang === l ? 'is-active' : ''}
              onClick={() => setLang(l)}
            >
              {l.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function Header({ t }) {
  const [open, setOpen] = useState(false);
  const items = ['work', 'services', 'process', 'faq', 'contact'];
  return (
    <header className="wrap header">
      <a href="#top" className="logo">
        {t.name}
        <span className="logo__sub">{t.brandSub}</span>
      </a>
      <button
        type="button"
        className="burger"
        aria-expanded={open}
        aria-controls="main-nav"
        onClick={() => setOpen(!open)}
      >
        {open ? t.close : t.menu}
      </button>
      <nav id="main-nav" aria-label="Menu" className={`nav ${open ? 'is-open' : ''}`}>
        {items.map((id) => (
          <a key={id} href={`#${id}`} onClick={() => setOpen(false)}>{t.nav[id]}</a>
        ))}
      </nav>
      <a href="#contact" className="btn btn--accent header__cta">{t.cta}</a>
    </header>
  );
}

function Hero({ t, showGroup }) {
  const h = t.hero;
  return (
    <section id="top" className="wrap hero">
      <div className="hero__mast">
        <p className="kicker">{h.kicker}</p>
        <h1 className="hero__title">
          {h.titleStart} <em>{h.titleAccent}</em> {h.titleEnd}
        </h1>
      </div>
      <div className="hero__body">
        <p className="lead hero__lead">{h.lead}</p>
        <ul className="facts">
          {h.facts.map((f) => (
            <li key={f}>{f.replace('{n}', projects.length)}</li>
          ))}
        </ul>
      </div>
      <p className="tasks__title">{h.tasksTitle}</p>
      <div className="tasks">
        {GROUPS.map((g, i) => (
          <button type="button" className="task" key={g} onClick={() => showGroup(g)}>
            <span className="task__num">{pad(i + 1)}</span>
            <span className="task__title">{t.groups[g].title}{' '}→</span>
            <span className="task__text">{t.groups[g].text}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function SectionHead({ title, meta, dark }) {
  return (
    <div className={`shead ${dark ? 'shead--dark' : ''}`}>
      <h2>{title}</h2>
      <p>{meta}</p>
    </div>
  );
}

function Work({ t, lang, filter, setFilter }) {
  const w = t.work;
  const list = filter === 'all' ? projects : projects.filter((p) => p.group === filter);
  return (
    <section id="work" className="wrap section">
      <SectionHead title={w.title} meta={w.meta} />
      <div className="chips" role="group" aria-label={w.title}>
        {['all', ...GROUPS].map((g) => (
          <button
            key={g}
            type="button"
            className={`chip ${filter === g ? 'is-active' : ''}`}
            aria-pressed={filter === g}
            onClick={() => setFilter(g)}
          >
            {g === 'all' ? t.groups.all : t.groups[g].title}
            <span className="chip__n">{g === 'all' ? projects.length : projects.filter((p) => p.group === g).length}</span>
          </button>
        ))}
      </div>
      <div className="cards">
        {list.map((p) => (
          <Card key={p.id} p={p} w={w} c={p[lang]} groupTitle={t.groups[p.group].title} />
        ))}
        {!list.length && <p className="muted">{w.empty}</p>}
      </div>
    </section>
  );
}

function Card({ p, w, c, groupTitle }) {
  const [open, setOpen] = useState(false);
  return (
    <article className="card">
      <a
        className={`card__img ${p.light ? 'card__img--light' : ''}`}
        style={{ background: p.color }}
        href={p.url || undefined}
        target="_blank"
        rel="noopener"
        tabIndex={-1}
        aria-hidden="true"
      >
        {p.image ? (
          <img src={p.image} alt="" loading="lazy" width="1440" height="900" />
        ) : (
          <span className="case__wm">{p.watermark}</span>
        )}
      </a>
      <div className="card__body">
        <p className="kicker">{groupTitle} · {c.kicker}</p>
        <h3>{c.title}</h3>
        <p className="muted">{c.lead}</p>
        <p className="card__result"><b>{w.result}:</b> {c.result}</p>
        {open && (
          <dl className="card__dl">
            <div><dt>{w.task}</dt><dd>{c.task}</dd></div>
            <div><dt>{w.solution}</dt><dd>{c.solution}</dd></div>
          </dl>
        )}
        <div className="card__actions">
          {p.url ? (
            <a href={p.url} className="btn btn--dark" target="_blank" rel="noopener">{w.open} ↗</a>
          ) : (
            <span className="case__soon">{w.soon}</span>
          )}
          {c.extra && (
            <a href={c.extra.href} className="btn btn--line" target="_blank" rel="noopener">{c.extra.label} ↓</a>
          )}
          <button type="button" className="linkbtn" aria-expanded={open} onClick={() => setOpen(!open)}>
            {open ? w.less : w.more}
          </button>
        </div>
      </div>
    </article>
  );
}

function Services({ t, discuss }) {
  const s = t.services;
  return (
    <section id="services" className="dark">
      <div className="wrap section">
        <SectionHead title={s.title} meta={s.meta} dark />
        <div className="packs">
          {s.items.map((it) => (
            <div className="pack" key={it.title}>
              <p className="kicker">{t.groups[it.group].title}</p>
              <h3>{it.title}</h3>
              <p className="pack__price">{s.from} {it.price} {s.currency}</p>
              <p className="pack__text">{it.text}</p>
              <ul className="pack__list">
                {it.includes.map((x) => <li key={x}>{x}</li>)}
              </ul>
              <p className="pack__term">{s.term}: {it.term}</p>
              <button type="button" className="btn btn--accent" onClick={() => discuss(`${it.title}: `)}>
                {s.order}
              </button>
            </div>
          ))}
        </div>
        <div className="extra">
          <p className="extra__title">{s.extraTitle}</p>
          <ul>
            {s.extra.map((x) => (
              <li key={x.title}><span>{x.title}</span><span>{x.price}</span></li>
            ))}
          </ul>
        </div>
        <p className="pack__note">{s.note}</p>
      </div>
    </section>
  );
}

function Process({ t }) {
  const p = t.process;
  return (
    <section id="process" className="wrap section">
      <SectionHead title={p.title} meta={p.meta} />
      <div className="steps">
        {p.steps.map((s, i) => (
          <div className="step" key={s.title}>
            <span className="step__num">{pad(i + 1)}</span>
            <h3>{s.title}</h3>
            <p className="muted">{s.text}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function About({ t }) {
  const a = t.about;
  return (
    <section id="about" className="about">
      <div className="wrap section about__in">
        {a.image && (
          <div className="about__photo">
            <img src={a.image} alt={t.name} loading="lazy" width="800" height="1000" />
          </div>
        )}
        <div className="about__text">
          <p className="kicker">{a.kicker}</p>
          <h2>{a.title}</h2>
          {a.paragraphs.map((x) => (
            <p className="lead" key={x}>{x}</p>
          ))}
        </div>
      </div>
    </section>
  );
}

function Faq({ t }) {
  const f = t.faq;
  return (
    <section id="faq" className="wrap section">
      <SectionHead title={f.title} meta={f.meta} />
      <div className="faq">
        {f.items.map((x) => (
          <details key={x.q}>
            <summary>{x.q}</summary>
            <p className="muted">{x.a}</p>
          </details>
        ))}
      </div>
    </section>
  );
}

function Contact({ t, lang, preset }) {
  const c = t.contact;
  const [status, setStatus] = useState('idle');

  async function onSubmit(e) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    if (!data.consent) { setStatus('consent'); return; }
    setStatus('sending');
    try {
      // text/plain — простой запрос без предварительной CORS-проверки
      const res = await fetch(site.leadApi, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify({
          site: 'myfreelab.ru', name: data.name, contact: data.contact, comment: data.message,
          page: window.location.href, website: data.website, lang,
        }),
      });
      if (!res.ok) throw new Error(res.status);
      setStatus('ok');
      form.reset();
    } catch {
      setStatus('fail');
    }
  }

  const note = { ok: c.ok, fail: c.fail, consent: c.needConsent }[status];

  return (
    <section id="contact" className="dark">
      <div className="wrap section contact">
        <div className="contact__info">
          <h2 className="contact__title">
            {c.titleStart} <em>{c.titleAccent}</em>
          </h2>
          <p className="lead">{c.lead}</p>
          <div className="contact__links">
            <a href={tg} target="_blank" rel="noopener">{c.telegram} · @{site.contacts.telegram}</a>
            <a href={`mailto:${site.contacts.email}`}>{c.email} · {site.contacts.email}</a>
          </div>
        </div>

        <form className="form" onSubmit={onSubmit}>
          <label htmlFor="f-name">{c.name}</label>
          <input id="f-name" name="name" required maxLength={80} autoComplete="name" placeholder={c.namePh} />
          <label htmlFor="f-contact">{c.contact}</label>
          <input id="f-contact" name="contact" required maxLength={120} placeholder={c.contactPh} />
          <label htmlFor="f-msg">{c.message}</label>
          <textarea id="f-msg" name="message" rows="4" required maxLength={2000} placeholder={c.messagePh} key={preset} defaultValue={preset} />
          <input className="hp" name="website" tabIndex={-1} autoComplete="off" aria-hidden="true" />
          <label className="consent">
            <input type="checkbox" name="consent" value="1" />
            <span>{c.consentStart} <a href="privacy.html" target="_blank" rel="noopener">{c.consentLink}</a></span>
          </label>
          <button type="submit" className="btn btn--accent" disabled={status === 'sending'}>
            {status === 'sending' ? c.sending : c.send}
          </button>
          <p className={`form__note ${status === 'ok' ? 'is-ok' : ''}`} role="status">{note}</p>
        </form>
      </div>
      <footer className="footer">
        <div className="wrap footer__in">
          <span>{t.footer}</span>
          <span className="footer__links">
            <a href="privacy.html">{t.privacy}</a>
            <a href="#top">{t.toTop} ↑</a>
          </span>
        </div>
      </footer>
    </section>
  );
}
