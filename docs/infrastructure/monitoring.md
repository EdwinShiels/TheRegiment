✅ Monitoring & Alerting

Monitoring tools will be added post-MVP.

Target Tools (later phase):
- `Logfire.dev` or `Sentry` for error capture
- `Prometheus` + `OpenTelemetry` for advanced metrics

Required now:
- Discord message failures must retry 3x and log as `status: missed`
- All missed events must be visible in Battle Station

Optional alerts for:
- Missed job triggers
- Discord API failures
- Unexpected DB schema violations
