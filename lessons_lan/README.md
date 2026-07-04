# Homeschool Lessons LAN App

`lessons_lan/` is the canonical HomeSchool Mastery app. It is a local-first
Flask/Jinja/SQLite web app that runs on a household computer and serves students
on the home LAN.

## What this app is

The app supports daily homeschool operations:

- student login for Charlie and Chris
- Today checklist and lesson detail pages
- lesson completion tracking
- TEKS/STAAR-aligned Math and Reading/ELAR practice
- snake practice, Fraction Battle, Text Detective, Discount Dash, Story Duel,
  Spelling Lab, and Vocabulary Signal Breaker
- XP, levels, Adventure page, mastery gates, boss fights, loot, and gear unlocks
- student feedback and admin feedback inbox
- admin lesson CRUD and password reset
- optional local Ollama lesson coach and Story Duel grading

## Domain

Family homeschool education and learner accountability, with local-first
TEKS/STAAR-aligned practice. See `../docs/DOMAIN_MODEL.md` for the complete
domain model.

## Quick start (Windows / PowerShell)

From this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

Then open on this PC:

- `http://127.0.0.1:5000`

To let tablets connect, use this PC's LAN IP (example):

- `http://192.168.1.50:5000`

## Shutdown

- Terminal run: press `Ctrl+C` in the terminal running `python run.py`.
- Startup-folder autostart: run `autostart/uninstall-startup-folder.ps1`, then
  stop the currently running Python process if it is still active.
- Scheduled Task autostart: run `autostart/uninstall-autostart.ps1`, then stop
  the currently running Python process if it is still active.

Do not delete the database to stop the app.

## Default accounts

On first run, the app creates a local SQLite database in `instance/homeschool.db` and seeds accounts:

- Admin: `admin` / `admin123`
- Charlie: `charlie` / `34086028`
- Chris: `chris` / `0822`

## Database location

On first run, the app creates a local SQLite database at:

```text
lessons_lan/instance/homeschool.db
```

Tests use temporary database paths through Flask app configuration.

### Reset everything (operator-only; wipes local progress)

`reset-db --yes` deletes and recreates the local SQLite database. Use it only for
operator maintenance after backing up learner data.

Stop the app first so the database file is not locked, then from this folder:

```powershell
.\.venv\Scripts\Activate.ps1
python -m flask --app run reset-db --yes
python run.py
```

Kids use **Today** -> **Practice** (quiz + XP) and **Adventure** for boss
fights. Practice items match **Math** and **Reading (ELAR)** lessons in the
seed bank.

Change passwords anytime (Admin -> Users).

## Verification

From this folder:

```powershell
pytest -q
```

Run targeted tests before changing mastery, XP, boss, gear, route separation, or
accountability behavior.

## Make it start automatically when you turn on the PC

### Recommended (no admin): Startup folder

Run this once (PowerShell):

```powershell
cd autostart
.\install-startup-folder.ps1
```

To remove it later:

```powershell
cd autostart
.\uninstall-startup-folder.ps1
```

(Commands assume your current directory is **`lessons_lan`**; from the repo root run `cd lessons_lan` first.)

### Optional (may require admin): Scheduled Task

Some Windows setups block `schtasks` without elevation.

Run (PowerShell):

```powershell
cd autostart
.\install-autostart.ps1
```

To remove it later:

```powershell
cd autostart
.\uninstall-autostart.ps1
```

## Notes

- This is meant for **home LAN use** (simple auth, no HTTPS).
- If Windows Firewall prompts you, allow Python for Private networks so tablets can reach the app.
- Optional Ollama features require a local Ollama server; the app has offline or
  heuristic fallback behavior for the current AI coach/Story Duel flows.

## Passdowns + task tracking

- App passdown: `PASSDOWN.md`
- App tasklist: `TASKLIST.md`
- Repository documentation index: `../docs/README.md`
- Repository task list: `../runtime/tasks/master_task_list.md`
