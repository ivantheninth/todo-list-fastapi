# End-to-end tests

`npm run test:e2e` starts the isolated Compose stack in
`../../docker-compose.e2e.yml`, runs Playwright against Nginx at
`https://localhost:8443`, then removes the containers, the temporary
certificate, and the anonymous PostgreSQL volume. The stack uses only the
`todolist_e2e` database and never reads the development or production database
configuration.

`npm run test:e2e` is the reliable default: it rebuilds the current frontend
and backend images before testing. `npm run test:e2e:fast` reuses the existing
`todolist-e2e-*` images and fails if any are absent. Use fast mode only for a
quick local rerun because it can test stale application code.

The default runner builds before starting containers and suppresses Docker's
verbose BuildKit stream so an interrupted terminal cannot block the build. A
non-zero build, startup, or Playwright exit code is still returned by the runner.

The local certificate is intentionally self-signed. Playwright ignores that
certificate error only for this E2E project, while the browser still receives a
real `Secure` cookie over HTTPS.

## Google OAuth

Do not automate a real Google account in this suite. Use a separate Google Cloud
test project with a dedicated OAuth client, a test-only callback URI, and a
non-production test account for an optional manually-run smoke test. Keep the
client secret outside the repository and revoke it after use. The existing
backend OAuth tests should continue to mock Google token exchange and ID-token
verification; this E2E suite deliberately does not navigate to Google.
