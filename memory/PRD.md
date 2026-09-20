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
- Env (backend/.env): X_CLIENT_ID, X_CLIENT_SECRET (SET 2026-09-18, real OAuth2 credentials), X_REDIRECT_URI=<preview>/api/x/auth/callback, FRONTEND_URL, X_TARGET_USERNAME=RobinityInt, X_TASK_TWEET_URL (EMPTY — the 'secret xlink' post to like/RT/quote), X_QUOTE_TEXT, X_DEV_MOCK=0 (dev-login disabled).
- X app must have callback URL = X_REDIRECT_URI, scopes: tweet.read users.read follows.read like.read offline.access.
- Frontend: /app/robinitypage/app/web/src/x-connect.jsx (XConnect in PublicHeader right side; Tasks button + avatar/@username after connect; Tasks modal -> EVM form once -> 3 task cards with intent open + Verify). Styles appended to styles.css. Rebuild with `npm run build:web` in /app/robinitypage.
- Tested: /app/test_reports/iteration_1.json (14/14 backend + full frontend flow pass, using dev mock login).

## Points + Leaderboard (2026-09-18)
- Points: follow 20, like_rt 10, quote 50 (TASK_POINTS in x_router.py). verify returns points_awarded; user doc gets points + points_updated_at; /me and /config expose points.
- GET /api/x/leaderboard (public): top 10 by points desc (tie → earlier completion), fields rank/username/profile_image_url/points/completed + total_participants. No EVM exposed.
- Frontend: "Leaderboard" button in header (always visible) → modal (medals for top 3, "you" highlight). Tasks panel shows points card + per-task badges; header Tasks button shows "N pts".
- Tested: /app/test_reports/iteration_2.json (8/8 backend + full frontend pass). Seed/dev users removed afterwards; X_DEV_MOCK back to 0.
- Real OAuth confirmed working: user @0xBombo connected and completed Follow (20 pts).

## Frontend migration to /app/frontend (2026-09-18, deploy fix)
- ROOT CAUSE of robinit.xyz placeholder: Emergent pipeline builds only /app/frontend (CRA). App lived in /app/robinitypage (esbuild + serve.js) → never built.
- FIX: ported UI into standard CRA: src/index.js → src/robinity/main.jsx; src/robinity/* (landing, x-connect, admin, css), src/risk-ui/* (Intelligence), src/site-theme.css, src/assets/robinity-logo.png (css mask), public/assets/{favicon,robinity-logo}.png. Deps added: ethers@6, three@0.186.0. `CI=true yarn build` OK. frontend/.env: DISABLE_ESLINT_PLUGIN=true.
- Supervisor `frontend` (craco start :3000) now serves the app; serve.js killed. /app/robinitypage is now DEAD CODE (kept; user has not decided on deletion).
- Deployer static scan flags `ethers` (used only by non-functional /admin wallet login) as "blockchain" BLOCKER — user asked (option a: remove ethers + stub /admin, b: keep); NO ANSWER YET. Previous deploy with ethers present built successfully.
- Mobile: task buttons are now real <a> links (iOS universal link → X app; Android intent://…package=com.twitter.android with browser fallback). X OAuth authorize (/i/oauth2/*) is explicitly EXCLUDED by X from app deep links (apple-app-site-association `NOT /i/oauth2/*`) → Connect X must happen in the mobile browser; cannot be forced into the X app.

## Backlog
- P0: User must provide X_TASK_TWEET_URL (post to like/RT/quote) and confirm callback URL is registered in X Developer Portal; user to test real OAuth in browser.
- P1: Admin backend (/api/auth/nonce, verify-wallet, totp-setup, verify-totp, /api/admin/api-keys) if user wants the admin workspace functional
- P2: landing-effects / risk-ui standalone builds (npm run build:landing, build:risk)
