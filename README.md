```python
mkdir pixel_rpg_todo && cd pixel_rpg_todo
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install django
django-admin startproject config .
python manage.py startapp quests

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
