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

## X Connect + Tasks (2026-09-18)
- Backend: /app/backend/x_router.py (FastAPI, prefix /api/x). Endpoints: GET /config, GET /auth/login (OAuth2 PKCE redirect to x.com), GET /auth/callback (token exchange, users/me w/ profile_image_url, sets httponly cookie ri_x_session 30d), GET /auth/dev-login (only when X_DEV_MOCK=1), GET /me, POST /logout, POST /evm (once only, 0x+40hex), POST /tasks/{follow|like_rt|quote}/verify (X API check; if API tier forbids (402/403) the claim is accepted with verified:false).
- Mongo collections: x_users, x_sessions, x_oauth_states.
- Env (backend/.env): X_CLIENT_ID, X_CLIENT_SECRET (EMPTY — user will provide), X_REDIRECT_URI=<preview>/api/x/auth/callback, FRONTEND_URL, X_TARGET_USERNAME=RobinityInt, X_TASK_TWEET_URL (EMPTY — the 'secret xlink' post to like/RT/quote), X_QUOTE_TEXT, X_DEV_MOCK=1 (set to 0 for production).
- X app must have callback URL = X_REDIRECT_URI, scopes: tweet.read users.read follows.read like.read offline.access.
- Frontend: /app/robinitypage/app/web/src/x-connect.jsx (XConnect in PublicHeader right side; Tasks button + avatar/@username after connect; Tasks modal -> EVM form once -> 3 task cards with intent open + Verify). Styles appended to styles.css. Rebuild with `npm run build:web` in /app/robinitypage.
- Tested: /app/test_reports/iteration_1.json (14/14 backend + full frontend flow pass, using dev mock login).

## Backlog
- P0: Paste real X_CLIENT_ID / X_CLIENT_SECRET and X_TASK_TWEET_URL into backend/.env, set X_DEV_MOCK=0, restart backend, test real OAuth.
- P1: Admin backend (/api/auth/nonce, verify-wallet, totp-setup, verify-totp, /api/admin/api-keys) if user wants the admin workspace functional
- P2: landing-effects / risk-ui standalone builds (npm run build:landing, build:risk)
