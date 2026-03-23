# Update GHL Calendar Days Out

## Objective
Automatically update the booking window ("days out") for two GHL calendars on a recurring weekly schedule via GitHub Actions.

## Calendars
1. **Roadmap Call with Renzo**
2. **Coaches & Creators Roadmap Call**

## Schedule (Central Time)
| Day       | Time     | Days Out |
|-----------|----------|----------|
| Thursday  | 11:55pm  | 4        |
| Friday    | 11:55pm  | 3        |
| Saturday  | 11:55pm  | 3        |
| Sunday    | 11:55pm  | 2        |

"Days out" = how far into the future someone can book (e.g., 2 = today and tomorrow only).

## Required Inputs
- `GHL_API_KEY` — GoHighLevel API key with `calendars.readonly` + `calendars.write` scopes
- `GHL_LOCATION_ID` — GHL sub-account location ID

For local use: set in `.env`. For CI: set as GitHub repository secrets.

## Tools
| Script | Purpose |
|--------|---------|
| `tools/ghl_list_calendars.py` | List calendars, find IDs, check current settings |
| `tools/ghl_update_days_out.py` | Update days-out on specific calendars by name |
| `tools/ghl_run_scheduled_update.py` | CI entry point — hardcodes calendar names, accepts `--days-out` |

## API Details
- Base URL: `https://services.leadconnectorhq.com`
- Auth header: `Authorization: Bearer <API_KEY>`
- Version header: `2021-04-15`
- Update field: `allowBookingFor` (integer) + `allowBookingForUnit` ("days")
- Endpoint: `PUT /calendars/{calendarId}`

## Setup Steps
1. Copy `.env.example` to `.env`, fill in `GHL_API_KEY` and `GHL_LOCATION_ID`
2. `pip install -r requirements.txt`
3. Test API access: `python tools/ghl_list_calendars.py`
4. Test update (dry run): `python tools/ghl_update_days_out.py --calendar-name "Roadmap Call with Renzo" --days-out 4 --dry-run`
5. Test update (real): `python tools/ghl_update_days_out.py --calendar-name "Roadmap Call with Renzo" --days-out 4`
6. Push to GitHub, add `GHL_API_KEY` and `GHL_LOCATION_ID` as repo secrets
7. Manually trigger the workflow via GitHub Actions UI to verify
8. Monitor first scheduled run in GitHub Actions logs

## Troubleshooting
- **401 Unauthorized** — API key expired or invalid. Regenerate in GHL settings.
- **422 Unprocessable** — The PUT endpoint rejects read-only fields like `id`, `locationId`, `formSubmitRedirectUrl`, and `openHours`. Only send the fields you want to update.
- **Calendar not found** — Name changed in GHL. Update `CALENDAR_NAMES` in `ghl_run_scheduled_update.py`.
- **Workflow didn't run** — GitHub Actions disables cron on inactive repos. A `keep_alive.yml` workflow runs weekly to prevent this. Also, cron can be delayed up to 15 min.
- **Wrong day detected** — DST shift. In winter (CST=UTC-6), crons fire at 5:55 AM UTC instead of 4:55 AM UTC, but still land at 11:55pm CT.

## Changing the Schedule
- To change times/days: edit `.github/workflows/update_days_out.yml` cron entries (UTC) and the day-of-week mapping in the "Determine days-out value" step.
- To change calendars: edit `CALENDAR_NAMES` in `tools/ghl_run_scheduled_update.py`.
- To change days-out values: edit the if/elif mapping in `.github/workflows/update_days_out.yml`.
