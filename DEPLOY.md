# Deploy to PythonAnywhere – Step by Step

## 1. Create Account
Go to https://www.pythonanywhere.com and sign up for a free account.

## 2. Create Web App
1. Log in and go to the **Web** tab
2. Click **Add a new web app**
3. Select **Manual configuration** (not Flask wizard)
4. Choose **Python 3.10** (or latest available)

## 3. Clone Your Repo
Open a **Bash console** from the PythonAnywhere dashboard and run:
```bash
cd ~
git clone https://github.com/aasz253/KioskKeeper.git
cd KioskKeeper
pip install --user Flask Flask-SQLAlchemy
```

## 4. Configure WSGI
1. Go back to the **Web** tab
2. Click the **WSGI configuration file** link
3. Delete everything and paste the contents of `wsgi.py` from this repo
4. Save the file

## 5. Set Working Directory
In the **Web** tab under **Code**:
- **Source code**: leave as default
- **Working directory**: set to `/home/YOUR_USERNAME/KioskKeeper`

## 6. Set Up Static Files
In the **Web** tab under **Static files**:
- Add URL: `/static/`
- Add Path: `/home/YOUR_USERNAME/KioskKeeper/static/`

## 7. Reload
Click the green **Reload** button in the Web tab.

Your app is now live at:
**https://YOUR_USERNAME.pythonanywhere.com**

---

## Notes
- Free accounts have a 512MB storage limit (enough for SQLite + app)
- The app will be accessible from any device on the internet
- SQLite database persists between sessions on PythonAnywhere
- Free tier apps may be paused after 3 months of inactivity — just log in and reload
