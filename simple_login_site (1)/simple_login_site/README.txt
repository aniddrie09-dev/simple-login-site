Simple Login Website

Run:
1. Install Python 3.
2. In this folder run: pip install -r requirements.txt
3. Change app.secret_key and the admin password in app.py.
4. Run: python app.py
5. Visit http://127.0.0.1:5000

Security note: the admin panel intentionally does NOT show passwords. Passwords are stored as one-way hashes, so even an administrator cannot read users' original passwords.
