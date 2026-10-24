import { useEffect, useState } from 'react';
import site from './content/site.json';
import projects from './content/projects.json';

const LANGS = ['ru', 'en'];
const pad = (n) => String(n).padStart(2, '0');

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
  const t = site[lang];

  useEffect(() => {
    document.documentElement.lang = lang;
    document.title =
      lang === 'ru'
        ? 'Алексей Ан — сайты, тексты и боты для малого бизнеса'
        : 'Alexey An — websites, copy and bots for small business';
    try {
      localStorage.setItem('lang', lang);
    } catch {
      /* ignore */
    }
  }, [lang]);

  return (
    <>
      <TopBar t={t} lang={lang} setLang={setLang} />
      <Header t={t} />
      <main>
        <Hero t={t} />
        <Services t={t} />
        <Work t={t} lang={lang} />
        <Quote t={t} />
        <Process t={t} />
        <About t={t} />
        <Contact t={t} lang={lang} />
      </main>
    </>
  );
}

function TopBar({ t, lang, setLang }) {
  return (
    <div className="topbar">
      <div className="wrap topbar__in">
        <span>{t.issue}</span>
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
  const items = ['services', 'work', 'process', 'about', 'contact'];
  return (
    <header className="wrap header">
      <a href="#top" className="logo">{t.name}</a>
      <nav aria-label="Menu" className="nav">
        {items.map((id) => (
          <a key={id} href={`#${id}`}>{t.nav[id]}</a>
        ))}
      </nav>
      <a href="#contact" className="btn btn--accent">{t.cta}</a>
    </header>
  );
}

function Hero({ t }) {
  const h = t.hero;
  return (
    <section id="top" className="wrap hero">
      <div className="hero__mast">
        <h1>{t.name}</h1>
      </div>
      <div className="hero__body">
        <div className="hero__main">
          <p className="kicker">{h.kicker}</p>
          <h2 className="hero__title">
            {h.titleStart} <em>{h.titleAccent}</em>
          </h2>
        </div>
        <div className="hero__side">
          <p className="lead">{h.lead}</p>
          <div className="btns">
            <a href="#work" className="btn btn--dark">{h.primary}</a>
            <a href={`https://t.me/${site.contacts.telegram}`} className="btn btn--line" target="_blank" rel="noopener">
              {h.secondary}
            </a>
          </div>
          <p className="coverline">{h.coverLine}</p>
        </div>
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

function Services({ t }) {
  const s = t.services;
  return (
    <section id="services" className="dark">
      <div className="wrap section">
        <SectionHead title={s.title} meta={s.meta} dark />
        <div className="toc">
          {s.items.map((it, i) => (
            <div className="toc__row" key={it.title}>
              <span className="toc__num">{pad(i + 1)}</span>
              <h3>{it.title}</h3>
              <p>{it.text}</p>
              <span className="toc__price">{s.from} {it.price} {s.currency}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Work({ t, lang }) {
  const w = t.work;
  return (
    <section id="work" className="wrap section">
      <SectionHead title={w.title} meta={`${w.meta} 01–${pad(projects.length)}`} />
      {projects.map((p, i) => (
        <Case key={p.id} p={p} i={i} w={w} c={p[lang]} />
      ))}
    </section>
  );
}

function Case({ p, i, w, c }) {
  return (
    <article className={`case ${i % 2 ? 'case--rev' : ''}`}>
      <div
        className={`case__img ${p.light ? 'case__img--light' : ''}`}
        style={{ background: p.color }}
      >
        {p.image ? (
          <img src={p.image} alt={c.title} loading="lazy" width="1440" height="900" />
        ) : (
          <>
            <span className="case__wm" aria-hidden="true">{p.watermark}</span>
            <span className="case__label">[{w.screenshot}]</span>
          </>
        )}
      </div>
      <div className="case__text">
        <p className="kicker">{w.case} {pad(i + 1)} · {c.kicker}</p>
        <h3>{c.title}</h3>
        <p className="muted">{c.lead}</p>
        <dl className="case__dl">
          <div><dt>{w.task}</dt><dd>{c.task}</dd></div>
          <div><dt>{w.solution}</dt><dd>{c.solution}</dd></div>
          <div><dt>{w.stack}</dt><dd>{p.stack.join(', ')}</dd></div>
        </dl>
        {p.url ? (
          <a href={p.url} className="case__link" target="_blank" rel="noopener">{w.open} →</a>
        ) : (
          <span className="case__soon">{w.soon}</span>
        )}
      </div>
    </article>
  );
}

function Quote({ t }) {
  return (
    <section className="quote">
      <div className="quote__in">
        <p className="quote__text">{t.quote.text}</p>
        <p className="kicker">{t.quote.author}</p>
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

const LEAD_API = import.meta.env.VITE_LEAD_API;

function Contact({ t, lang }) {
  const c = t.contact;
  const [status, setStatus] = useState('idle');

  async function onSubmit(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.currentTarget));

    if (!LEAD_API) {
      // Пока нет бэкенда — открываем почту с готовым письмом
      const body = `${c.name}: ${data.name}\n${c.contact}: ${data.contact}\n\n${data.message}`;
      window.location.href = `mailto:${site.contacts.email}?subject=${encodeURIComponent('Заявка с myfreelab.ru')}&body=${encodeURIComponent(body)}`;
      return;
    }

    setStatus('sending');
    try {
      const res = await fetch(LEAD_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, lang }),
      });
      if (!res.ok) throw new Error(res.status);
      setStatus('ok');
      e.target.reset();
    } catch {
      setStatus('fail');
    }
  }

  return (
    <section id="contact" className="dark">
      <div className="wrap section contact">
        <div className="contact__info">
          <h2 className="contact__title">
            {c.titleStart} <em>{c.titleAccent}</em>
          </h2>
          <p className="lead">{c.lead}</p>
          <div className="contact__links">
            <a href={`https://t.me/${site.contacts.telegram}`} target="_blank" rel="noopener">
              {c.telegram} · @{site.contacts.telegram}
            </a>
            <a href={`mailto:${site.contacts.email}`}>{c.email} · {site.contacts.email}</a>
          </div>
        </div>

        <form className="form" onSubmit={onSubmit}>
          <label htmlFor="f-name">{c.name}</label>
          <input id="f-name" name="name" required autoComplete="name" placeholder={c.namePh} />
          <label htmlFor="f-contact">{c.contact}</label>
          <input id="f-contact" name="contact" required placeholder={c.contactPh} />
          <label htmlFor="f-msg">{c.message}</label>
          <textarea id="f-msg" name="message" rows="4" required placeholder={c.messagePh} />
          <button type="submit" className="btn btn--accent" disabled={status === 'sending'}>
            {status === 'sending' ? c.sending : c.send}
          </button>
          <p className="form__note" role="status">
            {status === 'ok' && c.ok}
            {status === 'fail' && c.fail}
            {status === 'idle' && !LEAD_API && c.mailHint}
          </p>
        </form>
      </div>
      <footer className="footer">
        <div className="wrap footer__in">
          <span>{t.footer}</span>
          <span>myfreelab.ru</span>
        </div>
      </footer>
    </section>
  );
}
