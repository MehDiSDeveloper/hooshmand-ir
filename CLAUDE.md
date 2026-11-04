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
So far the geo-language redirect and the admin's file uploads
(`test_admin_upload.py`, which uses the database) are covered; the next three
worth pinning are named at the foot of this file.

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

## Detailed docs (read only the one your task touches)

Details live in `docs/agents/`. Before changing an area, read its file; after changing it, update that file in the same commit.

- `docs/agents/architecture.md`: content in the database, translation columns, URLs and the language prefix, Jalali/Gregorian dates, JavaScript as enhancement, the admin, where the site grows. Read before changing models, content, routes or JS.
- `docs/agents/design.md`: the design system (tokens, typography, components, layout). Read before any template or CSS change.
- `docs/agents/contact.md`: the contact form and the digital business card.

## Production: where and how this site is live

> A deploy changes the **live** site. Ask the user before deploying.

| | |
|---|---|
| URL | https://royahooshmand.ir (`www.` and `http://` redirect here) |
| Server | VPS `91.207.18.218` (Webdade, Ubuntu 24.04). From Windows: `ssh vps` → user `deploy` (key login, passwordless sudo, in the `docker` group) |
| App dir | `/srv/hooshmand-ir/`: code (replaced on every deploy), `.env` (production secrets, only on the server), `data/` (the volume; deploy never touches it) |
| Container | published on `127.0.0.1:8005` → 8000. Only Caddy is public (ports 80/443) |
| Reverse proxy | Caddy on the host, automatic Let's Encrypt HTTPS. Config source `G:\Repos\devops\server\caddy\Caddyfile`, applied with `bash /g/Repos/devops/caddy-apply.sh` |
| Runbook | `G:\Repos\devops\RUNBOOK.md` (server layout, logs, restart, backups, DNS). Keep it updated after any server change |

**Deploy** (Windows PowerShell; takes the **local working copy**, uncommitted changes included, git is not involved):

```
G:\Repos\devops\deploy.ps1 hooshmand-ir
```

It uploads the repo without `.git`, `.venv`, `node_modules`, `.next`, `.env*`, `data/` and the dev-only compose file,
strips CRLF from `*.sh`, rsyncs into `/srv/hooshmand-ir/` (keeping `.env` and `data/`), runs `docker compose up -d --build`
and waits for a 200 on `http://127.0.0.1:8005/healthz`. Migrations run in the container's start script, so there is no manual step.

**Compose on the server.** The server `.env` sets `COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml`, so a plain `docker compose …` in `/srv/hooshmand-ir` uses the prod override. `docker-compose.prod.yml` is not in this repo; it lives in `G:\Repos\devops\server\hooshmand-ir\` and is shipped by `deploy.sh`. It replaces the port with `127.0.0.1:8005`. `docker-compose.override.yml` is dev-only and is never uploaded.
If you change the service name, the container port or the published port here, update `G:\Repos\devops\`
(`deploy.sh`, `server/hooshmand-ir/`, the Caddyfile) in the same change, or the live site breaks.

**Production environment** lives only in `/srv/hooshmand-ir/.env` (mode 600). A new variable the code needs must be added there too,
not only to `.env.example`. Change a key without opening the file (it backs up `.env` and re-creates the container):
`printf 'KEY=value\n' | bash /g/Repos/devops/env-set.sh hooshmand-ir`. Never print, copy into chat or commit its values.

**Look at the live app:**

```
ssh vps "cd /srv/hooshmand-ir && docker compose ps && docker compose logs --tail 100"
```

**Backups:** `data/` is backed up every night (03:30) to `/var/backups/apps/` on the server and pulled daily to `G:\apps backup` on Windows; 14 days are kept in each place. How to restore: RUNBOOK → Backups.

**Specific to this app:**

- Uploads (`/media/`) are served by Django itself (`DJANGO_SERVE_MEDIA` defaults on); Caddy only proxies.
- Admin user `admin` was created once with `createsuperuser --noinput` from `DJANGO_SUPERUSER_*` in the server `.env`;
  its password can be changed in the admin afterwards.
- No bot.
- The live database started empty on 2026-09-30 with `seed_profile`. **Never run `seed_demo` on the server.**
- One-off commands: `ssh vps "cd /srv/hooshmand-ir && docker compose exec -T web python manage.py <cmd>"`.

## Deployment

One container, one process, one volume:

```
docker compose up --build     # or: docker build -t hooshmand . && docker run …
```

`start.sh` is the whole boot: `migrate`, then `collectstatic`, then gunicorn.
WhiteNoise serves static with a one-year cache and a hashed manifest outside
`DEBUG`. Uploads under `data/media/` are served by Django in every mode
(`apps.core.views.media`, one-day cache), because one container has no proxy in
front of it; set `DJANGO_SERVE_MEDIA=0` when nginx/Caddy serves `/media/`
instead — **if uploads 404 on the host, that is the thing to check first.**

**`DEBUG` defaults to off.** `settings.py` reads `.env` itself (without
overriding real environment variables), so `runserver` still gets
`DJANGO_DEBUG=1` from `.env` locally; a missing variable in production can no
longer ship tracebacks. `/healthz` is exempt from the HTTPS redirect so the
container's own plain-HTTP probe works.

Environment variables are documented in `.env.example`. Only two matter:
`DJANGO_SECRET_KEY` (rotating it logs out every admin session) and
`DJANGO_ALLOWED_HOSTS`. Set `DJANGO_SITE_URL` to the real domain — the canonical
tag, the `hreflang` alternates, the sitemap and **the QR code** all read it, so
a wrong value ships a QR pointing at the wrong host.

## Things that will bite

- **Persian text on an `/en/` or `/de/` page is an empty `_en`/`_de`
  column, not a code bug** — `tr()` falls back to Persian. Never POST part
  of an admin form from a script: Django saves every field the POST leaves
  out, unless it has a default, as empty. That is how montazeri-ir and
  hesam-ir lost their profile's English and German on 2026-09-30. Edit in
  the admin from a browser (it sends every field) or in `manage.py shell`.
- **`{# … #}` in a Django template is single-line only.** A multi-line one
  leaks into the rendered page as visible text. Use `{% comment %}` for
  anything over one line — every long comment in `templates/` already does.
- **Every views module that renders a translated field must load `site_tags`.**
  `{% load site_tags %}` at the top; forgetting it is a render-time error, not
  a silent miss.
- **Every Persian column is required, even one declared `blank=True`.**
  `@i18n_fields` sets `blank` per language and overwrites the factory's, so a
  Profile form (or a test posting to it) must fill every `<field>_fa`.
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
