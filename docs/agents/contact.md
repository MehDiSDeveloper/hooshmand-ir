<!-- Moved out of CLAUDE.md so it loads only when needed. Keep it current. -->

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
