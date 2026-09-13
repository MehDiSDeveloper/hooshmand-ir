# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository.

## What this is

The personal site of **Roya Hooshmand**, a social media and content
strategist — a portfolio of case studies, a blog and a digital business card in
one Django app, in **three languages** (Persian, English, German). It is also
the link and the QR code she hands people, so the two things it must never be
are slow and ugly.

It began as a copy of `montazeri-ir` (Mahdi Montazeri's site) and keeps that
project's code and design system. What differs is the content, the names and
storage keys, the ports, the Instagram channel and the vocabulary of the
ambient background — so a fix to the shared code usually belongs in both repos.

The stance of the whole project: **a strong front end over a deliberately
small back end.** Nine views, one SQLite file, no API, no build step, no
JavaScript framework. Every design decision below exists to keep it that way
while still allowing the site to grow.

## Commands

Everything runs through the venv at `.venv/` (`.venv/Scripts/` on Windows).

```bash
.venv/Scripts/python manage.py runserver 8025       # local dev
.venv/Scripts/python manage.py migrate               # after any model change
.venv/Scripts/python manage.py makemigrations content
.venv/Scripts/python manage.py seed_profile          # the REAL content, idempotent
.venv/Scripts/python manage.py seed_profile --wipe   # replace projects/skills/roles
.venv/Scripts/python manage.py seed_demo             # placeholder content — overwrites the real profile
.venv/Scripts/python manage.py seed_demo --wipe      # start the content over
.venv/Scripts/python manage.py createsuperuser       # to reach /admin/
.venv/Scripts/python manage.py check
docker compose up --build                            # the real thing, port 8005
```

**The ports are picked so this site runs beside the others on this machine.**
`montazeri-ir` answers on 8004 (docker) and 8021 (runserver); the other
projects hold 8000–8003 and 8011–8024. This one is **8005** in docker and
**8025** for `runserver`, written in `docker-compose.yml`,
`.claude/launch.json` and `DJANGO_CSRF_TRUSTED_ORIGINS` in `.env`.

Tests live in `tests/` and run with `.venv/Scripts/python manage.py test tests`.
They are `SimpleTestCase`s so `pytest-django` can pick them up unchanged later.
So far only the geo-language redirect is covered; the next three worth pinning
are named at the foot of this file.

## The shape of the project

```
config/        settings, urls, wsgi          — the whole Django configuration
apps/core/     views, forms, i18n strings, template tags, jalali
apps/content/  models, admin, seed command   — everything a visitor reads
templates/     base.html + one file per page
static/        site.css, app.js, self-hosted fonts
data/          db.sqlite3, media/, staticfiles/  — THE one volume in production
```

`data/` is the only directory that survives a redeploy, and everything
persistent is inside it on purpose: the database, uploads and collected static
are one mount, so hosting is one container and one disk.

## Content lives in the database, not in the code

**`seed_profile` is the real content and `seed_demo` will overwrite it.** Both
write `Profile.load()`, so running `seed_demo` on a live database replaces
Roya's biography with placeholders. `seed_profile` is the reviewed record of
every public claim — it is the file to edit when a claim changes, not the admin
form, because the admin leaves no diff. Its docstring says where every number
comes from (the Insights screenshots in her case study), which résumé claims
are left out because nothing backs them, and why the birth date and the phone
number are absent. It also deletes everything inherited from `montazeri-ir`, so
it is safe to run without `--wipe`.

`apps/content/models.py` holds every word a visitor reads. Nothing else in the
project contains copy — if you find yourself typing a sentence about Roya into
a template, it belongs in a model field instead.

Eight models: `Profile` (a singleton — `Profile.load()` is the only reader),
`SkillGroup`/`Skill`, `Tag`, `Project`, `Experience`, `Post`, `Message`.

Two deliberate absences:

- **`Skill` has no percentage.** A "90% Python" bar is a number nobody can
  verify and every reviewer discounts. `is_primary` is the only emphasis there
  is, and it means "show this in the hero strip".
- **There is no view counter and no "years of experience" field.** Both are
  claims a personal site cannot back up.

## Translation: one column per language

A translated field is **one real column per language**, named `<field>_<lang>`.
`@i18n_fields(...)` in `models.py` writes those columns so the model body stays
readable, and `Translatable.tr("title")` reads the active language with a
fallback chain that ends at Persian.

Why not `django-modeltranslation` or a per-language row: one dependency fewer,
every query stays a plain query with no join, the stock admin renders the three
inputs side by side for free, and **a fourth language is one entry in
`settings.LANGUAGES` plus one migration**. The cost is that an unfilled
language falls back rather than 404s, which is the behaviour a personal site
wants anyway.

In templates it is `{{ project|tr:"title" }}` and, for a Markdown field,
`{{ project|md:"body" }}`.

**UI strings are a different problem and have a different answer.** Buttons,
labels and section headings live in `apps/core/i18n.py` as one Python dict,
read with `{% t "nav.projects" %}`. Django's gettext catalogues need `.po`
files compiled by the `msgfmt` binary, which turns "reword a button" into a
build step that has to run on Windows, in CI and inside the image; this
vocabulary is about a hundred short strings. `LocaleMiddleware` is still what
activates the language — only the catalogue is ours.

**An unknown key renders as the key**, visibly, rather than as an empty string.

## URLs, and the language prefix

`i18n_patterns` with `prefix_default_language=False`: Persian is at `/`,
English at `/en/`, German at `/de/`. Everything a reader can see is inside that
block so a language switch is a real, shareable, indexable URL.

Machine endpoints stay **outside** it — `sitemap.xml`, `robots.txt`,
`feed.xml`, the `.vcf` and `/healthz`. There is nothing to translate about a
vCard, and a crawler should find one sitemap rather than three. That one
sitemap still lists every page in all three languages: `apps/core/sitemaps.py`
sets `i18n`, `alternates` and `x_default`, so each URL carries its hreflang
siblings — which is how the `/de/` pages get found by someone searching in
German.

The header nav is in the order a reviewer reads a candidate — work, résumé,
about, writing — with contact as the one button in the bar. **The footer is the
site map**: every page grouped as explore / career / connect, plus the vCard,
RSS and `sitemap.xml`.

The switcher is built in `apps/core/context_processors.py` with Django's
`translate_url`, so it points at *this* page in the other language instead of
dumping the reader on the home page.

**A first visit picks its language by country.** `GeoLanguageMiddleware`
(`apps/core/middleware.py`) sends a first-time visitor on an unprefixed page
from Germany to `/de/…` and from any other *known* non-Iranian country to
`/en/…`; the mapping is `GEO_LANGUAGE_BY_COUNTRY` in settings. The country
comes from `apps/core/geo.py`: a proxy header (`DJANGO_GEO_COUNTRY_HEADER`)
first, then a MaxMind-format database at `data/geoip/country.mmdb`. The rules
that keep it from doing harm, all pinned in `tests/test_geo_language.py`:
it decides **once** (cookie `hooshmand_geo`, set whether or not it redirected,
so the switcher's «فارسی» link sticks); it never redirects an explicit `/en/`
or `/de/` URL, a POST, a same-site Referer, or a **crawler** — redirecting
Googlebot (which crawls from the US) would de-index the Persian pages; and an
**unknown country changes nothing**, so a missing database never sends Iran to
English. `hreflang="x-default"` points at the unprefixed URL for this reason.

## The design system

**Colour lives in the three token blocks at the top of `static/css/site.css`
and nowhere else.** `:root` is the light theme; the two blocks after it restate
the same names for dark, once for `prefers-color-scheme` and once for an
explicit `[data-theme="dark"]`, so an explicit choice beats the device in both
directions. A rule that needs a tint writes `rgba(var(--rose-rgb), .12)`, never
a second hex. Re-theming the site is editing values in those blocks. The two
`--bg` values are also written in `base.html`'s `theme-color` meta tags and in
`THEME_COLOR` in `app.js`.

The palette is **four pastels, each with one meaning**. They are Roya's own
colours — pink, purple, salmon/peach-pink and magenta — on a blush paper ground
(light) or a deep plum (dark), with plum ink rather than blue-black. The site
was re-themed from montazeri-ir's mint/sky/peach/lilac to this set, so the
token names differ between the two repos.

| hue | colour | means | where |
|---|---|---|---|
| rose (`--rose`) | صورتی, pink | the work, and anything actionable | projects, nav, primary buttons |
| lavender (`--lavender`) | بنفش, purple | the career | timeline, résumé, facts |
| coral (`--coral`) | کالباسی / گلبهی, salmon | the person | availability, «این روزها», contact |
| orchid (`--orchid`) | ارغوانی / سرخابی, magenta | writing, and nothing else | posts, so a post tag never reads as a project |

A fifth hue would need a fifth meaning, which is the reason not to add one.

**Nothing has a hard corner.** Buttons, chips, tags, the header bar and nav are
pills; icon tiles and small buttons are circles; the portrait, the faces and
the cover art use `--blob`, an organic radius; bullets and eyebrows carry a
`--sparkle` and a few headings a `--heart`. The two marks are SVG masks defined
once in `:root`, so they take any colour through `background`. The animations
and the ambient background are untouched by the re-theme — only colour and
shape changed.

**Each hue is a five-step ramp, not one value**: `--x-tint`, `--x-soft`,
`--x`, `--x-strong`, `--x-deep`, plus `--x-rgb` for tints. A card, its border,
its icon and its label can be one colour at four intensities. What each step
is *for* is the rule to keep:

- `-tint` is a ground you can barely see, `-soft` is a fill, `--x` is the
  pastel itself (a button, a dot, a hover border).
- **Only `-strong` and `-deep` may colour a letterform**: `-strong` on
  `--surface` or `-tint` (≥ 5.4:1 in this palette), and **on a `-soft` fill
  only `-deep`** (≥ 6.6:1) — keep that rule even where `-strong` happens to
  pass, so a later retune of a ramp cannot quietly break it.
- Text **on the pastel `--x` itself is `--on-accent`**, which is ink. That is
  why a primary button is a pastel with dark lettering rather than a saturated
  fill with white: it keeps the page pastel and still AA (8:1 or better).

In dark the ramp inverts — `-deep` is the *lightest* step — so a rule that
asked for `-deep` because it was drawing text keeps getting the readable step
without knowing about the theme.

**`--accent-*` is an indirection, not a fifth colour.** An element carrying
`data-accent="coral"` (or `"lavender"`, `"orchid"`, `"rose"`) re-points the whole
ramp for itself and everything inside it, so every eyebrow, pill, chip, tag,
button and link in that subtree follows. Re-colouring a section is one
attribute in the template and no new CSS. Prefer `var(--accent-…)` over
`var(--rose-…)` in any component that could appear in more than one context.

**Where a hue *carries* something it means something; where it is only a
field it is rhythm.** Tags, links, buttons and post rows are the first kind and
keep the meanings above. Rows of near-identical boxes — case covers, project
cards, skill groups, fact tiles, contact channels, footer columns, the tech
ribbon — are the second: their container carries **`.rhythm`**, whose children
take turns through all four hues, so four boxes read as four boxes. Removing
the class is how a row goes back to one hue.

**A section can be a band.** `.sec.sec-band` paints the section edge to edge in
its own accent's `--wash-*` with a hairline dot texture. Bands alternate with
plain sections down the home page (work → *career band* → toolbox → *writing
band* → contact), which is what gives a long page a horizontal rhythm.

**Nothing may bleed sideways.** The hero aurora is an element with
`overflow: hidden`, and `.page-head::before` bleeds *up* behind the
transparent header but has `inset-inline: 0`. A negative inline inset or a
`left: -9999px` is scrollable overflow in RTL: the Persian page opens shifted
by exactly that much, while English looks fine. `html` carries
`overflow-x: clip` as the last line of defence, and **`<body>` must not carry
any `overflow-x`** — next to `clip` on `html` it turns `<body>` into its own
scroll container and the sticky header stops sticking.

**`[hidden]` always wins** (`display: none !important` in the base). Without
it a component's own `display: grid` beats the attribute, and a closed
popover, a filtered-out card and the pre-JS back-to-top button all show.

**Motion has one vocabulary.** Two easings, `--ease` (settle) and `--spring`
(a small overshoot, for things that pop); hover lifts use `transform`, arrivals
use the individual `translate`/`scale` properties, so the two never overwrite
each other. **The whole site sits on `.ambient`** (first child of `<body>`): a
fixed, self-clipped layer of four pastel lights drifting on 22–32 s cycles,
turned by scroll through a scroll-driven `rotate` (no JS), plus grain; over
them `initAmbient()` draws a canvas network (linked nodes, events travelling
the links, rising marketing and social media terms — `WORDS` in `app.js`,
English in every language) in the `--x-rgb` colours. Strength is the
`--ambient` and `--net` tokens, set per theme. Every decorative loop —
the ambient field, the aurora drift, the portrait halo, the
floating skill chips, the tech ribbon — sits behind
`prefers-reduced-motion`, which also stops the ribbon and wraps it.

**Logical properties only.** The site runs RTL in Persian and LTR in English
and German from the same rules: `padding-inline-start`, never `padding-left`.
A rule with a physical side in it is a bug in one of the three languages.

**Three typefaces, all self-hosted.** Vazirmatn for everything Persian and all
UI, Fraunces for Latin display (the name, the card index, the error code) and
IBM Plex Mono for labels, dates and technology names. Nothing this page draws
with comes off a CDN — inside Iran `fonts.googleapis.com` is slow at best.
Latin runs inside Persian text carry `.lat` or `.mono`, which set
`direction: ltr; unicode-bidi: isolate`, or a Latin word flips inside a Persian
sentence.

**The theme has three states**, not two: `system` / `light` / `dark`, stored
under `localStorage["hooshmand-theme"]`. That key is read **twice**: by
`app.js`, and by a small blocking script in `base.html`'s `<head>`. The second
one is pre-paint on purpose — deferring it to `app.js` repaints one frame in,
which is exactly the flash it prevents. **If you rename the key, rename it in
both places.**

## JavaScript is enhancement, and only enhancement

`static/js/app.js` is one file, no dependency, no build. Turn JavaScript off
and every link, form and page still works; what is lost is polish.

Thirteen concerns, each its own function started from `boot()`: theme; the
ambient network; header
(frosting, reading progress, back-to-top, mobile nav); nav indicator;
popovers; tooltips; reveal-on-scroll; pointer effects; tag filter;
copy-to-clipboard; share; the contact form's counter and sending state;
command palette.

**The search button carries no "Ctrl K" hint**, on purpose: in Chrome that
chord belongs to the address bar and searches Google, so a hint under the icon
promised something the page cannot deliver. The palette still opens on `/`.

The rules worth keeping:

- **Reveal-on-scroll's resting state is visible.** The hidden state exists only
  while `.js` is on the root element and motion is allowed. No observer, or
  `prefers-reduced-motion`, and everything is simply shown — content parked at
  `opacity: 0` waiting for a callback that never fires is the classic way this
  feature fails silently. The arrival is a CSS *animation* staggered by `--d`,
  not a transition with an inline `transition-delay`: that delay would also
  delay every hover on the card for the rest of the visit.
- **Tooltips are `data-tip="…"`, and they decorate a name the element already
  has.** One floating element, placed in viewport pixels, flipped below when
  there is no room above, clamped to both edges; mouse hover and keyboard focus
  only. An icon button still needs its `aria-label` — on touch that label is
  all there is.
- **Pointer effects are fine-pointer only and off under reduced motion.**
  `data-spot` is the soft light that follows the pointer inside a card (it uses
  the card's `::after`, so a spotlit component must not need its own);
  `data-tilt="n"` tilts by up to n degrees (the portrait, the business card).
- **The tag filter is client-side because the whole list is already on the
  page.** The query string is kept in step so a filtered view is still
  shareable, and the chip for `?tag=` is pressed on a cold load. If the list
  ever outgrows one render, this becomes a server-side filter and the chips
  become links. The count on each chip comes from `_tags_for()` in
  `apps/content/views.py`.

The command palette (Ctrl/⌘+K, or `/`) reads its index (`cmdk_index`) from the
context processor, shipped inside the page as JSON, so opening it costs no
request and it can never disagree with what the site actually has. Each entry
carries `i`, an icon id from `templates/partials/icons.html`. The language and
theme shortcuts are read from the header itself. It costs two small queries per
request; if the site grows past a few hundred rows, cache the list — do not
make the palette fetch.

## Dates: Jalali for Persian, Gregorian for the rest

Storage stays Gregorian and UTC. **Every date a Persian reader sees is rendered
Jalali by the server**, through `apps/core/jalali.py` (pure arithmetic, no
dependency) and the `smart_date` filter — so the first paint is already correct
and nothing has to be repaired by JavaScript a frame later. English and German
readers get the Gregorian date and their own month names. Persian digits come
from `fa_num`, which is a no-op in the other two languages.

How long a role ran is the `{% duration start end %}` tag: whole months counted
inclusively, the way a CV counts them — "2 yrs 5 mos", "2 J. 5 Mon.",
"۲ سال و ۵ ماه". It is arithmetic on the two dates printed beside it, not a
stored claim, so there is still no years-of-experience field anywhere.

## The contact form

`POST` → save → `redirect` with `?sent=1`, so a refresh can never resend.
Protection is a **honeypot** (`website`, invisible inside the form's own box
via `.hp` — never `left: -9999px`, which scrolls the Persian page sideways) plus a
per-session 60-second throttle from `settings.CONTACT_RATE_LIMIT_SECONDS`. No
captcha: for the volume a personal site attracts, a field a human never sees is
enough, and it costs the reader nothing.

A spam submission is answered **with the same redirect a real one gets**. A bot
that can tell the difference will tune around the trap.

Nothing is emailed. Messages land in the database and are read at
`/admin/content/message/`. Adding email means one `send_mail` in
`apps.core.views.contact` and SMTP settings — deliberately not done, because an
SMTP credential in a container is a real cost and the admin list already works.

## The digital business card

`/card/` is one screen made to be handed over, and `/card/hooshmand.vcf` is a
real vCard so a phone saves the contact rather than a screenshot. The QR is
rendered **server-side** by `segno` as inline SVG: it prints, it survives a
screenshot, and it needs no JavaScript to exist.

`segno` will not accept `currentColor`, so the code is drawn in a sentinel hex
and swapped in `apps/core/views.py`. That is what lets one SVG be legible in
both themes without rendering the QR twice.

## The admin, and the panel that is coming

`django.contrib.admin` is registered and is the **interim** way to edit
content. The lightweight custom panel is a later piece of work; when it is
built it belongs in `apps/panel/` as its own app with its own templates,
reusing `site.css`'s tokens, and the stock admin can then be switched off in
one line. Until then, do not build admin-shaped branches into the public pages
— the two audiences are different and the panel is a screen of its own.

## Deployment

One container, one process, one volume:

```
docker compose up --build     # or: docker build -t hooshmand . && docker run …
```

`start.sh` is the whole boot: `migrate`, then `collectstatic`, then gunicorn.
WhiteNoise serves static with a one-year cache and a hashed manifest outside
`DEBUG`. Uploads under `data/media/` are served by Django in `DEBUG` and by the
front proxy or WhiteNoise in production — **if uploads 404 on the host, that is
the thing to check first.**

Environment variables are documented in `.env.example`. Only two matter:
`DJANGO_SECRET_KEY` (rotating it logs out every admin session) and
`DJANGO_ALLOWED_HOSTS`. Set `DJANGO_SITE_URL` to the real domain — the canonical
tag, the `hreflang` alternates, the sitemap and **the QR code** all read it, so
a wrong value ships a QR pointing at the wrong host.

## Where this grows, and how

Each of these is a small, contained change. None needs the design above
rewritten:

- **A fourth language.** One entry in `settings.LANGUAGES`, one migration, one
  column in `apps/core/i18n.py`'s dict, one entry in `templatetags`' month names.
- **The lightweight admin panel.** `apps/panel/`, see above.
- **Email on a new message.** One `send_mail` call in `contact`.
- **Photos on projects.** The field is already there (`Project.cover`); the
  card and the detail page already render it when present.
- **A `/now` page.** `Profile.now_*` already holds the sentence; a page would
  be a longer version of the same field.
- **Postgres.** One dict in `settings.DATABASES` and `psycopg` in
  `requirements.txt`. Nothing in the app knows which backend it is on. Do this
  when concurrent writes get heavy or a second machine needs the same data —
  not before, because a separate database is the single biggest line on the
  hosting bill.
- **Tests.** The three worth writing first: every route answers 200 in all
  three languages; `Translatable.tr` falls back rather than returning empty;
  and the contact form's honeypot and throttle both refuse without saving.

## Things that will bite

- **`{# … #}` in a Django template is single-line only.** A multi-line one
  leaks into the rendered page as visible text. Use `{% comment %}` for
  anything over one line — every long comment in `templates/` already does.
- **Every views module that renders a translated field must load `site_tags`.**
  `{% load site_tags %}` at the top; forgetting it is a render-time error, not
  a silent miss.
- **`Profile.save()` forces `pk = 1`.** There is one person on a personal site.
  Do not try to create a second row.
- **`data/` is in `.gitignore` and `.dockerignore`.** The database is never
  committed and never baked into the image.
- **Every key in `Profile.links` needs two things**: an icon `#i-<key>` in
  `templates/partials/icons.html` and a label `channel.<key>` in
  `apps/core/i18n.py`. The key for mail is `email`, not `mail` — both icon ids
  exist for that reason. `instagram` is the one channel this site adds over
  `montazeri-ir`; it also feeds `Profile.social_urls` (JSON-LD `sameAs`), the
  footer's connect column and the vCard. A missing icon is an empty button; a missing label
  renders as the key.
- **The QR plate is light in both themes** (`--qr-plate`, `--qr-ink`, defined
  once in `:root`). Do not "fix" it to follow dark mode: many phone cameras
  cannot read a light-on-dark code.
- **In the preview pane, a hidden or covered window pauses animation frames,
  CSS animations and `IntersectionObserver`.** Screenshots of a scrolled page
  then come back blank and the header never reports `is-stuck`. That is the
  pane, not the page — check with computed styles, or inject a style that
  zeroes animation and add `.is-in` to every `.reveal` before capturing.
