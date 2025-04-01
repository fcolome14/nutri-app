# 🥗 Django Nutrition Tracker App

A full-featured Django web application to track your daily nutrition intake and generate calorie/macronutrient history graphs using PostgreSQL as the backend and `uv` for environment management.

---

## 🚀 Features

- Add meals with quantity and date
- Calculate total kcal, protein, carbs, and fats per meal
- Track daily nutrition intake
- Plot interactive historical graphs with Plotly
- Admin panel for managing users and food database
- Uses `.env` for secure config
- Easy setup using `init_db.py` and optional Makefile

---

## 📦 Requirements

- Python 3.10+
- PostgreSQL (locally installed or Docker)
- `uv` package manager: [Install UV](https://github.com/astral-sh/uv)

---

## 🧰 Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/nutrition-tracker.git
cd nutrition-tracker
```

### 2. Create `.env` file
```bash
DB_NAME=nutrition_db
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DEBUG=True
SECRET_KEY=your_django_secret_key
```

### 3. Set up the virtual environment
```bash
uv venv
source .venv/Scripts/activate   # Windows
# or
source .venv/bin/activate       # Linux/macOS
```

### 4. Install dependencies
```bash
uv install
```

### 5. Initialize the Database
Automatically create the database (if not exists) and run migrations:
```bash
python init_db.py
```

### 6. Create Admin User
Automatically create the database (if not exists) and run migrations:
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
Automatically create the database (if not exists) and run migrations:
```bash
python manage.py runserver
```
Then open your browser and navigate to:

- 🏠 Homepage: http://127.0.0.1:8000/

- ➕ Add meal: http://127.0.0.1:8000/add/

- 📊 View history: http://127.0.0.1:8000/history/

- 🔐 Login: http://127.0.0.1:8000/accounts/login/

- 🛠️ Admin panel: http://127.0.0.1:8000/admin/

### Project Structure
```bash
nutrition-tracker/
├── meals/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       ├── base.html
│       └── meals/
│           ├── home.html
│           ├── add_meal.html
│           └── history.html
├── nutrition_tracker/
│   └── settings.py
├── .env
├── init_db.py
├── manage.py
└── Makefile (optional)
```
### 💡 Tips
- Use `uv pip list` to view installed packages

- Use `uv pip freeze > requirements.txt` to export if needed

- Use pgAdmin to visually inspect your PostgreSQL database