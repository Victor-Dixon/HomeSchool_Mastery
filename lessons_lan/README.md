# Homeschool Lessons (simple LAN app)

In the [HomeSchool_Mastery](https://github.com/Victor-Dixon/HomeSchool_Mastery) monorepo, this code lives in **`lessons_lan/`** (sibling to the Node **Mastery** app at the repo root).

This is a tiny web app you run on your PC so your kids can open it from their tablets and see **today's lessons**.

## What it does

- Kid login (e.g. Charlie / Chris)
- Shows **Today** with a simple checklist
- Marks items complete/incomplete
- Admin login to add/edit lessons

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

## Default accounts

On first run, the app creates a local SQLite database in `instance/homeschool.db` and seeds accounts:

- Admin: `admin` / `admin123`
- Charlie: `charlie` / `34086028`
- Chris: `chris` / `0822`

### Reset everything (fresh lessons + XP / progress wiped)

Stop the app first (so the database file is not locked), then from the repo folder:

```powershell
.\.venv\Scripts\Activate.ps1
python -m flask --app run reset-db --yes
python run.py
```

Kids use **Today** → **Practice** (quiz + XP) and **Adventure** for boss fights. Practice items match **Math** and **Reading (ELAR)** lessons in the seed bank.

Change passwords anytime (Admin → Users).

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

## Passdowns + task tracking

- Repo passdown: `PASSDOWN.md`
- Repo tasklist: `TASKLIST.md`
- Cross-project master task DB (local tool): `C:\Users\USER\master-tasks-hub\master_tasks.py`
