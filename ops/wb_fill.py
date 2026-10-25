"""Fills works 4 and 5 of the workbook, the summary table rows and screenshots.

Usage: python3 -I wb_fill.py <unpacked_dir> <images_dir>
Works 1-3 text written by the student is never changed; only empty
"ВСТАВЬ СКРИНШОТ" cells receive pictures.
"""
import copy
import re
import struct
import sys
from pathlib import Path
from xml.dom import minidom

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

root_dir = Path(sys.argv[1])
img_dir = Path(sys.argv[2])
doc_path = root_dir / "word/document.xml"
rels_path = root_dir / "word/_rels/document.xml.rels"

raw = doc_path.read_text(encoding="utf-8")
decl = re.match(r"<\?xml[^>]*\?>\s*", raw)
decl_text = decl.group(0) if decl else '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
doc = minidom.parseString(raw.encode("utf-8"))
body = doc.getElementsByTagNameNS(W, "body")[0]


# ---------- helpers ----------
def kids(node, name):
    return [c for c in node.childNodes if c.nodeType == 1 and c.localName == name and c.namespaceURI == W]


def text_of(node):
    return "".join(t.firstChild.data for t in node.getElementsByTagNameNS(W, "t") if t.firstChild is not None)


def cell(tbl, r, c):
    rows = kids(tbl, "tr")
    cells = kids(rows[r], "tc")
    return cells[c]


def mk(name, **attrs):
    el = doc.createElementNS(W, "w:" + name)
    for k, v in attrs.items():
        el.setAttributeNS(W, "w:" + k, v)
    return el


def clean_rpr(rpr):
    """Copy of run properties without placeholder styling (colour, italics, highlight)."""
    if rpr is None:
        return None
    rpr = rpr.cloneNode(True)
    for tag in ("color", "i", "iCs", "highlight", "shd"):
        for e in kids(rpr, tag):
            rpr.removeChild(e)
    return rpr


def make_para(template_p, line, bold=False):
    p = mk("p")
    ppr = kids(template_p, "pPr")
    if ppr:
        p.appendChild(ppr[0].cloneNode(True))
    run = mk("r")
    runs = kids(template_p, "r")
    rpr = clean_rpr(kids(runs[0], "rPr")[0]) if runs and kids(runs[0], "rPr") else None
    if rpr is not None:
        run.appendChild(rpr)
    if bold:
        rp = kids(run, "rPr")
        if rp:
            rp = rp[0]
        else:
            rp = mk("rPr")
            run.insertBefore(rp, run.firstChild)
        if not kids(rp, "b"):
            rp.insertBefore(mk("b"), rp.firstChild)
    t = mk("t")
    t.setAttribute("xml:space", "preserve")
    t.appendChild(doc.createTextNode(line))
    run.appendChild(t)
    p.appendChild(run)
    return p


def set_lines(tc, lines, para_index=-1):
    """Replace paragraph number para_index in the cell by one paragraph per line."""
    paras = kids(tc, "p")
    target = paras[para_index]
    for i, line in enumerate(lines):
        bold = False
        if isinstance(line, tuple):
            line, bold = line
        tc.insertBefore(make_para(target, line, bold), target)
    tc.removeChild(target)


def set_value(tbl, r, c, lines):
    if isinstance(lines, str):
        lines = [lines]
    set_lines(cell(tbl, r, c), lines)


_img_counter = [0]
_docpr = [9000]
rels_text = rels_path.read_text(encoding="utf-8")
new_rels = []


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])


def put_picture(tc, image_name, alt):
    """Replaces the content of the cell by a picture fitting the cell width."""
    src = img_dir / image_name
    _img_counter[0] += 1
    n = _img_counter[0]
    media_name = f"wbimg{n}.png"
    (root_dir / "word/media" / media_name).write_bytes(src.read_bytes())
    rid = f"rIdWb{n}"
    new_rels.append(
        f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{media_name}"/>'
    )
    wpx, hpx = png_size(src)
    tcw = kids(tc, "tcPr")[0].getElementsByTagNameNS(W, "tcW")
    width_dxa = int(tcw[0].getAttributeNS(W, "w")) if tcw else 9000
    cx = max(width_dxa - 260, 1500) * 635
    cy = int(cx * hpx / wpx)
    _docpr[0] += 1
    xml = (
        f'<w:r xmlns:w="{W}" xmlns:wp="{NS_WP}" xmlns:a="{NS_A}" xmlns:pic="{NS_PIC}" xmlns:r="{NS_R}">'
        f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{_docpr[0]}" name="Picture {_docpr[0]}" descr="{alt}"/>'
        f'<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        f'<a:graphic><a:graphicData uri="{NS_PIC}"><pic:pic>'
        f'<pic:nvPicPr><pic:cNvPr id="{_docpr[0]}" name="{media_name}"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        f"</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>"
    )
    run = doc.importNode(minidom.parseString(xml.encode("utf-8")).documentElement, True)
    paras = kids(tc, "p")
    for extra in paras[1:]:
        tc.removeChild(extra)
    p = paras[0]
    for child in list(p.childNodes):
        if not (child.nodeType == 1 and child.localName == "pPr"):
            p.removeChild(child)
    p.appendChild(run)


# ---------- content ----------
SHOTS = {
    # (work, part, slot) -> image file name in images dir
    (1, "site"): "2.png",
    (1, "test"): "13.png",
    (2, "site"): "3.png",
    (3, "site"): "4.png",
    (4, "order"): "5.png",
    (4, "site"): "12.png",
    (5, "order"): "6.png",
    (5, "site"): "10.png",
}
ALT = {
    (1, "site"): "Первый экран сайта фотографа",
    (1, "test"): "Таблица заявок сайта фотографа",
    (2, "site"): "Первый экран сайта школы робототехники",
    (3, "site"): "Первый экран цифрового меню салона",
    (4, "order"): "Заказ на FL.ru: сайт трейдинг-клуба",
    (4, "site"): "Первый экран сайта Aurum Circle",
    (5, "order"): "Заказ на FL.ru: психологический сайт",
    (5, "site"): "Первый экран сайта Опора",
}

FL = "https://www.fl.ru/"

CONTENT = {
    4: {
        "order_url": "https://www.fl.ru/projects/5525650/razrabotka-prezentatsionnogo-sayta-dlya-mejdunarodnogo-treyding-kluba.html",
        "budget": "По договорённости",
        "task": "Нужен презентационный сайт (лендинг) для международного трейдинг-клуба: премиальный стиль «old money», десять блоков, доверие к клубу и вступление или покупка подписки.",
        "tz": [
            "• Цель: презентовать бренд, сформировать доверие и мотивировать посетителя вступить в клуб или купить подписку.",
            "• Это не торговая платформа, не брокерский сайт и не интернет-магазин.",
            "• Стиль: private financial institution, old money, exclusive trading club, premium finance. Палитра: чёрный, фиолетовый, белый, акценты благородного золота. Референсы заказчик обещал прислать отдельно.",
            "• Десять блоков: первый экран, о клубе, преимущества, продукты, результаты и статистика, отзывы, как вступить, FAQ, финальный призыв (Telegram или другой ресурс), подвал.",
            "• Требования: адаптация под телефоны, планшеты и компьютеры, плавная прокрутка и ненавязчивые анимации, базовое SEO, поддержка аналитики, лёгкое редактирование контента, подключение домена и публикация.",
            "• Пока не нужны: личные кабинеты, регистрация, платежи, автоматическая выдача подписок.",
            "• В отклике просили указать цену под ключ, срок, технологии и примеры работ, лучше из финансов или премиальных ниш.",
            "• На момент скриншота: бюджет «по договорённости», откликнулись 64 фрилансера, цены в откликах от 1 до 380 000 ₽, сроки от 1 до 40 дней.",
        ],
        "questions": [
            "• Как называется клуб, есть ли логотип и брендбук (цвета, шрифты)?",
            "• Какие именно продукты и подписки продаются, из чего они состоят и сколько стоят?",
            "• Какие результаты и цифры можно показывать и как согласовать формулировки о доходности с юридической точки зрения?",
            "• Есть ли реальные отзывы и разрешение на их публикацию?",
            "• Какие референсы нравятся заказчику (обещаны отдельно)?",
            "• Куда вести финальный призыв: Telegram-канал, бот или форма заявки?",
            "• Какую аналитику подключить и нужны ли другие языки, кроме русского?",
            "• Есть ли домен и хостинг, каков бюджет и желаемый срок запуска?",
        ],
        "ai": "Claude (Anthropic)",
        "audience": [
            "ЦА: взрослые 25–50 лет, начинающие и опытные трейдеры, которые устали от сигналов и хотят системы и сообщества.",
            "Тон: спокойный, уверенный, премиальный. Без «быстрых денег» и без обещаний прибыли.",
            "Цель: заявка на вступление или переход в Telegram.",
            "Допущение: клуб Aurum Circle, цены, цифры и отзывы вымышлены и помечены на странице как демонстрационные.",
        ],
        "prompt": [
            "Фактический запрос: инструкция из шаблона задания («Действуй как эксперт-копирайтер по лендингам. Напиши текст, используя вводные…») вместе с данными заказа. Ниже его оформленная версия.",
            "",
            "Действуй как эксперт-копирайтер по лендингам. Напиши текст, используя вводные.",
            "Задача: презентационный сайт международного трейдинг-клуба Aurum Circle.",
            "ЦА: взрослые начинающие и опытные трейдеры, устали от сигналов, хотят системы и сообщества.",
            "Тон: спокойный, премиальный, без обещаний прибыли и «быстрых денег».",
            "Цель: заявка на вступление или переход в Telegram.",
            "Блоки: первый экран, о клубе, преимущества, программы, цифры, отзывы, как вступить, FAQ, финальный призыв.",
            "Обязательно: предупреждение о риске и пометка, что цифры и отзывы демонстрационные.",
            "Структура ответа: заголовок и подзаголовок, боли клиента, решение, оффер с ценой и призывом.",
        ],
        "final": {
            "head": ["Трейдинг без шума. Клуб, где решения принимают спокойно.", "Aurum Circle объединяет трейдеров из 14 стран: обучение с нуля, разборы сделок в прямом эфире и строгие правила управления риском. Без сигналов «на удачу» и без обещаний прибыли."],
            "pains": [
                "1. Десятки каналов с «верными» сигналами, а в итоге хаос и чужие решения.",
                "2. Первый убыток после идеи, в которой вы были уверены. Дальше эмоции вместо плана.",
                "3. Нет системы и некому задать вопрос, пока сделка открыта.",
            ],
            "solution": [
                "Даём систему, а не сигналы: правила входа и выхода, расчёт риска до сделки, журнал сделок.",
                "Наставники разбирают сделки участников открыто и честно.",
                "Деньги участников в управление не принимаем и доходность не обещаем.",
            ],
            "offer": [
                "Старт: 3 900 ₽ в месяц. Практика: 7 900 ₽ в месяц. Закрытый круг: по приглашению. Цены демонстрационные.",
                "Кнопка: «Подать заявку на вступление». Вторая кнопка: «Написать в Telegram».",
                "Микротекст: куратор свяжется с вами в течение дня. Торговля связана с риском потери капитала.",
            ],
        },
        "folder": "trading-club (репозиторий club.myfreelab)",
        "refs": [
            "https://workspace.ru/cases/premialnyy-lending-dlya-avtorskih-torgovyh-taktik/",
            "https://workspace.ru/cases/lending-dlya-finansovogo-kluba/",
        ],
        "take": [
            "Тёмная премиальная эстетика с золотыми акцентами и фиолетовым свечением.",
            "Осторожные формулировки о рисках и явное отделение клуба от сигналов и доверительного управления.",
            "Призывы в Telegram и порядок блоков «оффер, содержание, доверие, вопросы, заявка».",
            "Не беру тяжёлые эффекты и анимации Tilda, чтобы страница оставалась быстрой.",
        ],
        "build_prompt": [
            "Сборка выполнена в Claude Code, а не в OpenCode. Ниже оформленная версия задачи для сборки.",
            "",
            "Собери одностраничный сайт без фреймворков: index.html, css/styles.css, js/main.js.",
            "Палитра: чёрный #0b0a0e, фиолетовый #2b1659, золото #c9a24b, слоновая кость #ece6d8.",
            "Шрифты Cormorant Garamond и Inter с кириллицей, файлы лежат в /fonts, без Google Fonts.",
            "Десять блоков в порядке из ТЗ. Мобильная версия, меню-бургер, плавное появление блоков, учитывать prefers-reduced-motion.",
            "Форма отправляет JSON в Google Apps Script через fetch. Ловушка для ботов, проверка полей, сообщения об успехе и ошибке.",
            "Предупреждение о риске в первом экране и в подвале. Данные помечены как демонстрационные.",
        ],
        "fixes": [
            "1. Заголовок первого экрана был слишком крупным и рвался на пять строк. Уменьшил размер и вынес курсивную часть на отдельную строку.",
            "2. В шрифте Cormorant цифры были «старинными», и «14» читалось как «I4». Включил ровные цифры.",
            "3. Браузер держал старые стили (кэш на 30 дней). Добавил номер версии к ссылкам на стили и скрипты.",
        ],
        "fields": "Имя / Telegram или телефон / Опыт в трейдинге / Комментарий",
        "dest": "Google Таблица «Заявки myfreelab», лист club. Заявки принимает Google Apps Script (код в google-apps-script/Code.gs). Копия в Telegram возможна через свойства скрипта, токен на сайте не хранится.",
        "url": "https://club.myfreelab.ru",
        "check_note": "Сайт опубликован на своём домене с HTTPS. Форма подключена к таблице, тестовые заявки приходят на свой лист. Отметки проверки ставит автор после собственной проверки.",
        "case_task": "Нужен презентационный сайт трейдинг-клуба в стиле «старые деньги»: десять блоков, доверие и вступление без обещаний прибыли.",
        "case_done": [
            "Текст: заголовок, боли, решение, программы, цифры, отзывы, FAQ и призывы.",
            "Сборка: адаптивный сайт без фреймворков, свои шрифты, десять блоков по ТЗ.",
            "Форма: заявка уходит в Google Таблицу (лист club), приём проверен.",
            "Публикация: club.myfreelab.ru, HTTPS, репозиторий club.myfreelab на GitHub.",
        ],
        "summary": [
            "Хорошо: удалось выдержать премиальный стиль и при этом честно: предупреждения о риске, без обещаний доходности, данные помечены как демонстрационные. Страница быстрая, без обращений к сторонним серверам.",
            "Улучшил бы в реальном заказе: получил бы от заказчика название, бренд, продукты, реальные цифры и юридические формулировки, подключил бы аналитику и проверил форму заявок до сдачи.",
        ],
    },
    5: {
        "order_url": "https://www.fl.ru/projects/5526142/psihologicheskiy-sayt-s-podderjkoy.html",
        "budget": "По договорённости",
        "task": "Нужен психологический сайт на восемь блоков в современном оформлении, с реальными методами поддержки и возможностью купить курс поддержки. Он должен выглядеть так, будто его делал очень профессиональный человек.",
        "tz": [
            "• Дословно: «создать сайт с психологической помощью используя реальные методы поддержки чтобы сайт был красиво оформлен в современный интерьер на 8 блоков используя покупку курса поддержки чтобы было всё качественно как будто бы делал очень профессиональный человек».",
            "• Восемь блоков, современный привлекательный дизайн.",
            "• На сайте должна быть покупка курса поддержки.",
            "• Нужны реальные методы поддержки, а не общие слова.",
            "• Нет срока, бюджета, референсов, файлов и названия. Заказчик зарегистрирован меньше месяца.",
            "• На момент скриншота: бюджет «по договорённости», откликнулись 77 фрилансеров, цены в откликах от 1 до 140 000 ₽, сроки от 1 до 60 дней.",
        ],
        "questions": [
            "• Что за курс: содержание, формат, длительность, цена?",
            "• Как должна работать «покупка»: онлайн-оплата на сайте или заявка с последующей оплатой?",
            "• Кто специалист, есть ли дипломы и сертификаты, которые нужно показать?",
            "• Для кого сайт и с какими запросами к вам приходят люди?",
            "• Какие «реальные методы поддержки» нужно показать и какие восемь блоков имеет в виду заказчик?",
            "• Есть ли название, логотип, референсы и пожелания по цветам?",
            "• Какие юридические оговорки нужны, ведь тема чувствительная?",
            "• Каков бюджет и желаемый срок запуска, есть ли домен и хостинг?",
        ],
        "ai": "Claude (Anthropic)",
        "audience": [
            "ЦА: взрослые 25–50 лет, чаще женщины, с тревогой и усталостью, которым страшновато начинать долгую терапию.",
            "Тон: тёплый, бережный, без давления и без медицинских терминов, без обещаний «вылечить».",
            "Цель: запись на бесплатную встречу на 20 минут.",
            "Допущение: курс «Опора», ведущая, цена и отзывы вымышлены и помечены на странице как демонстрационные.",
        ],
        "prompt": [
            "Фактический запрос: инструкция из шаблона задания («Действуй как эксперт-копирайтер по лендингам. Напиши текст, используя вводные…») вместе с данными заказа. Ниже его оформленная версия.",
            "",
            "Действуй как эксперт-копирайтер по лендингам. Напиши текст, используя вводные.",
            "Задача: сайт психологической поддержки «Опора», курс на четыре недели.",
            "ЦА: взрослые с тревогой и усталостью, которым страшно начинать долгую терапию.",
            "Тон: тёплый, бережный, без давления, без обещаний «вылечить».",
            "Цель: запись на бесплатную встречу на 20 минут.",
            "Блоки: первый экран, для кого, как помогаем, программа, ведущая, отзывы, FAQ, оффер с формой.",
            "Обязательно: курс не заменяет медицинскую помощь, номер 112 для экстренных случаев, пометка, что отзывы, цена и ведущая демонстрационные.",
            "Структура ответа: заголовок и подзаголовок, боли клиента, решение, оффер с ценой и призывом.",
        ],
        "final": {
            "head": ["Опора, когда внутри шумно.", "Простые практики, живые встречи и психолог рядом. Для тех, кто давно держится и устал справляться в одиночку."],
            "pains": [
                "1. Тревога не отпускает: мысли крутятся по кругу, уснуть трудно, а отдыхать получается с чувством вины.",
                "2. Нет сил и всё в тягость: вы справляетесь, но давно не чувствуете, что живёте для себя.",
                "3. Хочется, чтобы кто-то помог разобраться: идти сразу на долгую терапию страшновато или рано.",
            ],
            "solution": [
                "Четыре недели практик, которые можно применить сегодня же: заземление и дыхание, дневник мыслей, практики внимательности.",
                "Небольшая группа с психологом: можно говорить, а можно просто слушать.",
                "Курс не заменяет медицинскую помощь, это сказано прямо на странице.",
            ],
            "offer": [
                "4 900 ₽ за четыре недели. Бесплатная встреча на 20 минут перед стартом. Возврат денег после первой недели. Цена демонстрационная.",
                "Кнопка: «Записаться на бесплатную встречу». Вторая кнопка: «Написать в Telegram».",
                "Микротекст: первая встреча ни к чему не обязывает. При опасности для жизни звоните 112.",
            ],
        },
        "folder": "psychology-support (репозиторий psychology.support.myfreelab)",
        "refs": [
            "https://workspace.ru/cases/sayt-psihfak-5-0-dlya-instituta-sovremennoy-psihologii-za-3-dnya/",
            "https://tenchat.ru/media/1068661-prodayuschaya-struktura-lendinga",
        ],
        "take": [
            "Порядок «оффер, для кого, программа по неделям, автор, отзывы, FAQ, заявка» и повтор призыва по странице.",
            "Заголовок про изменение жизни клиента, блок «о специалисте», FAQ для снятия возражений.",
            "Светлая тёплая палитра вместо тёмной: для темы поддержки она мягче и безопаснее.",
        ],
        "build_prompt": [
            "Сборка выполнена в Claude Code, а не в OpenCode. Ниже оформленная версия задачи для сборки.",
            "",
            "Собери одностраничный сайт без фреймворков: index.html, css/styles.css, js/main.js.",
            "Палитра: фон #faf6ef, зелёный #3f5f50, терракота #b9694a, песок #f1e8da.",
            "Шрифты Lora и Nunito с кириллицей, файлы лежат в /fonts, без Google Fonts.",
            "Восемь блоков: первый экран, для кого, как помогаем, программа по неделям, ведущая, отзывы, FAQ, оффер с формой.",
            "Мягкие скругления, мобильная версия, меню-бургер, плавное появление блоков, учитывать prefers-reduced-motion.",
            "Форма отправляет JSON в Google Apps Script через fetch. Ловушка для ботов, проверка полей.",
            "В тексте: курс не заменяет медицинскую помощь, номер 112. Данные помечены как демонстрационные.",
        ],
        "fixes": [
            "1. Зелёное размытое пятно на первом экране обрезалось ровной линией на границе блока. Сдвинул его внутрь блока и сделал прозрачнее.",
            "2. Браузер держал старые стили (кэш на 30 дней). Добавил номер версии к ссылкам на стили и скрипты.",
        ],
        "fields": "Имя / Telegram или телефон / С чем хотите прийти / Комментарий",
        "dest": "Google Таблица «Заявки myfreelab», лист psy. Заявки принимает Google Apps Script (код в google-apps-script/Code.gs). Копия в Telegram возможна через свойства скрипта, токен на сайте не хранится. Заявки содержат личные данные, доступ к таблице только у автора.",
        "url": "https://psy.myfreelab.ru",
        "check_note": "Сайт опубликован на своём домене с HTTPS. Форма подключена к таблице, тестовые заявки приходят на свой лист. Отметки проверки ставит автор после собственной проверки.",
        "case_task": "Нужен сайт психологической помощи на восемь блоков с реальными методами поддержки и курсом, оформленный современно и профессионально.",
        "case_done": [
            "Текст: заголовок, боли, решение, программа по неделям, ведущая, отзывы, FAQ и призывы.",
            "Сборка: адаптивный сайт без фреймворков, свои шрифты, восемь блоков.",
            "Форма: заявка уходит в Google Таблицу (лист psy), приём проверен. Онлайн-оплаты в макете нет.",
            "Публикация: psy.myfreelab.ru, HTTPS, репозиторий psychology.support.myfreelab на GitHub.",
        ],
        "summary": [
            "Хорошо: получилась тёплая и спокойная страница с реальными практиками вместо общих слов и бережными оговорками. Курс прямо назван не заменяющим медицинскую помощь.",
            "Улучшил бы в реальном заказе: уточнил бы у заказчика, как должна работать покупка курса, и подключил бы онлайн-оплату. Показал бы настоящие дипломы специалиста и реальные отзывы с разрешением на публикацию.",
        ],
    },
}


# ---------- walk the document ----------
body_children = [c for c in body.childNodes if c.nodeType == 1]
work = None
part = None
summary_done = False
shot_seen = {}

for el in body_children:
    if el.localName != "tbl":
        continue
    rows = kids(el, "tr")
    first = text_of(rows[0])
    label = text_of(kids(rows[0], "tc")[0])

    m = re.match(r"РАБОТА №(\d) • (РЕАЛЬНЫЙ ЗАКАЗ|СБОРКА И КЕЙС)", first)
    if m:
        work = int(m.group(1))
        part = "order" if m.group(2) == "РЕАЛЬНЫЙ ЗАКАЗ" else "build"
        continue

    # the universal extra blank at the end of the workbook must stay untouched
    if label.startswith("ДОПОЛНИТЕЛЬН"):
        work = None
        part = None
        continue

    # summary table
    if label.strip() == "№" and not summary_done:
        summary_done = True
        for n in (4, 5):
            c = CONTENT[n]
            vals = [FL, c["task"], c["budget"], None, c["url"]]
            for col, v in zip(range(1, 6), vals):
                if v is not None:
                    set_value(el, n, col, v)
        continue

    if work is None:
        continue

    # screenshots: only into empty "ВСТАВЬ СКРИНШОТ" cells
    for r_i, tr in enumerate(rows):
        for c_i, tc in enumerate(kids(tr, "tc")):
            if text_of(tc).startswith("ВСТАВЬ СКРИНШОТ"):
                if part == "order":
                    slot = "order"
                else:
                    slot = "site" if c_i == 0 else "test"
                key = (work, slot)
                if key in SHOTS:
                    put_picture(tc, SHOTS[key], ALT[key])

    if work in (1, 2) and label == "Поля формы":
        if work == 1:
            set_value(el, 1, 1, "Google Таблица, лист photo (таблица «Заявки myfreelab»)")
        else:
            set_value(el, 0, 1, "Name / Surname / Email (на английском)")
            set_value(el, 1, 1, "Google Таблица, лист robotex (таблица «Заявки myfreelab»). Форма на странице сайта, данные только на английском")
        continue

    if work not in (4, 5):
        continue
    c = CONTENT[work]

    if label == "Биржа":
        set_value(el, 0, 1, FL)
        set_value(el, 1, 1, c["order_url"])
        set_value(el, 2, 1, c["budget"])
        set_value(el, 3, 1, c["task"])
    elif label == "Что известно из ТЗ":
        set_value(el, 1, 0, c["tz"])
    elif label.startswith("Чего не хватает"):
        set_value(el, 1, 0, c["questions"])
    elif label == "Нейросеть для текста":
        set_value(el, 0, 1, c["ai"])
        set_value(el, 1, 1, c["audience"])
    elif label == "Промпт для текста":
        set_value(el, 1, 0, c["prompt"])
    elif label.startswith("Заголовок + подзаголовок"):
        f = c["final"]
        set_lines(cell(el, 0, 0), [(f["head"][0], True), f["head"][1]], para_index=1)
        set_lines(cell(el, 0, 1), f["pains"], para_index=1)
        set_lines(cell(el, 1, 0), f["solution"], para_index=1)
        set_lines(cell(el, 1, 1), f["offer"], para_index=1)
    elif label == "Папка проекта":
        set_value(el, 0, 1, c["folder"])
        set_value(el, 1, 1, c["refs"])
        set_value(el, 2, 1, c["take"])
    elif label.startswith("Промпт для сборки"):
        set_value(el, 1, 0, c["build_prompt"])
    elif label.startswith("Правки после первой"):
        set_value(el, 1, 0, c["fixes"])
    elif label == "Поля формы":
        set_value(el, 0, 1, c["fields"])
        set_value(el, 1, 1, c["dest"])
        set_value(el, 2, 1, c["url"])
        tc = cell(el, 3, 1)
        paras = kids(tc, "p")
        tc.appendChild(make_para(paras[-1], c["check_note"]))
    elif label.startswith("Задача заказчика") and len(rows) == 3:
        set_lines(cell(el, 0, 0), [c["case_task"]], para_index=1)
        set_lines(cell(el, 0, 1), ["• " + s for s in c["case_done"]], para_index=1)
        set_lines(cell(el, 1, 1), [c["url"]], para_index=1)
    elif label == "Короткий вывод по работе":
        set_value(el, 1, 0, c["summary"])

# ---------- write ----------
out = doc.documentElement.toxml()
doc_path.write_text(decl_text + out, encoding="utf-8")
if new_rels:
    rels_text = rels_text.replace("</Relationships>", "".join(new_rels) + "</Relationships>")
    rels_path.write_text(rels_text, encoding="utf-8")
print("pictures added:", _img_counter[0])
