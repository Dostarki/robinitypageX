# PRD — Robinity Intelligence (cloned repo)

## Original Problem Statement
https://github.com/Dostarki/robinitypage repoyu çek ve çalıştır (clone and run the repo)

## Architecture
- Repo cloned to /app/robinitypage (React 19 + esbuild, ethers, three.js)
- Built via `npm run build` (scripts/build-web.js → app/web/dist with hashed assets)
- Served by /app/robinitypage/serve.js (Node static server, SPA fallback) on port 3000
- Supervisor `frontend` program stopped; robinity serve.js occupies port 3000 (nohup, log: /var/log/robinity-serve.log)
- Preview URL: https://robinity-preview.preview.emergentagent.com

## What's Implemented (2026-09-18)
- Repo cloned, deps installed, web bundle built (entry JS 65.8 KB gzip)
- All routes verified 200: /, /intelligence, /legal, /methodology, /contact, /console
- Landing page verified visually via screenshot

## Known Limitations
- Repo is frontend-only. Admin page (/admin) calls /api/auth/* and /api/admin/* endpoints that DO NOT exist in the repo — admin workspace will show API errors.
- ETH price widget uses public Coinbase API (external).

## Changelog
- 2026-09-18: "Open Intelligence" buttons (landing hero, methodology, console) no longer navigate to /intelligence. They open an English toast via ComingSoonButton (landing.jsx, React portal to body): "Coming soon. Intelligence will be announced shortly — stay tuned on X (@robinityint)." Auto-dismiss 6s + close button. Toast CSS in styles.css (.ri-soon-toast). data-testids: open-intelligence-soon-button, soon-toast, soon-toast-close, soon-toast-x-link.

## Backlog
- P1: Admin backend (/api/auth/nonce, verify-wallet, totp-setup, verify-totp, /api/admin/api-keys) if user wants the admin workspace functional
- P2: landing-effects / risk-ui standalone builds (npm run build:landing, build:risk)
