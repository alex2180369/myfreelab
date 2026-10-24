# myfreelab.ru — портфолио Алексея Ан

Одностраничный сайт-витрина на React + Vite. Русская и английская версии, кейсы из одного файла.

## Где что менять

| Что | Файл |
|---|---|
| Кейсы (проекты) | `src/content/projects.json` |
| Все тексты RU/EN, цены, Telegram, почта | `src/content/site.json` |
| Цвета, шрифты, отступы | `src/styles.css` (переменные в начале) |
| Скриншоты и фото | `public/images/` |
| Заголовок и описание для поиска и превью | `index.html` |

### Как добавить проект

Скопируйте блок в `projects.json` и поменяйте поля:

```json
{
  "id": "coffee-shop",
  "url": "https://coffee.myfreelab.ru",
  "image": "/images/coffee-shop.webp",
  "color": "#2A1E17",
  "watermark": "Кофе",
  "stack": ["React", "Nginx"],
  "ru": { "kicker": "Лендинг", "title": "Кофейня", "lead": "…", "task": "…", "solution": "…" },
  "en": { "kicker": "Landing page", "title": "Coffee shop", "lead": "…", "task": "…", "solution": "…" }
}
```

- `url` пустой — вместо кнопки «Открыть сайт» будет «Скоро онлайн».
- `image` пустой — показывается цветная заглушка цвета `color`.
- `"light": true` — для светлой заглушки (тёмная подпись).

## Первый запуск (Windows)

1. Установите Node.js LTS: https://nodejs.org
2. Распакуйте проект, откройте папку в PowerShell и выполните:

```powershell
npm install
npm run dev
```

Сайт откроется на http://localhost:5173 и будет обновляться при каждом сохранении файла.

## Публикация на сервер

Один раз на сервере (под `mylab`):

```bash
sudo chown -R mylab:mylab /var/www/myfreelab.ru
sudo apt install -y rsync
```

Дальше каждый раз на своём компьютере, из папки проекта:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\deploy.ps1
```

Скрипт соберёт проект, загрузит его на сервер и заменит старую версию.

## Ускорение и кэш в Nginx (один раз)

Скопируйте `deploy/myfreelab-static.conf` на сервер и подключите — инструкция в начале файла.

## Форма заявки

Пока бэкенда нет, кнопка «Отправить заявку» открывает почтовую программу с готовым письмом.
Когда будет готов FastAPI, создайте `.env` по образцу `.env.example` — форма начнёт отправлять заявки на API.
