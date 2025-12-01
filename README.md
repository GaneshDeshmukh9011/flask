# Flask Blog (Two-tier) - Full Project

## Quick start

1. Create virtualenv and activate
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Mac/Linux
   .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize DB and create admin
   ```bash
   python -c "from app import app, db; from models import User; from extensions import bcrypt;\nwith app.app_context():\n  db.create_all();\n  if not User.query.filter_by(username='admin').first():\n    pw = bcrypt.generate_password_hash('adminpass').decode('utf-8');\n    u = User(username='admin', email='admin@example.com', password=pw, is_admin=True);\n    db.session.add(u);\n    db.session.commit();\n    print('Admin created: admin / adminpass')"
   ```

4. Run
   ```bash
   python app.py
   ```

Open http://127.0.0.1:5000
