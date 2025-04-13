## Create Virtual Environment
```
python -m venv .venv
```

## Install Requirements
```
pip install -r requirements.txt
```

## Collect Static
```
python manage.py collectstatic
```

## Database
```
python manage.py migrate
```

## Create Superuser
```
pyhton manage.py createsuperuser
```

## Запуск проект
- Локально 
```
python manage.py runserver
```

- Докер 
```
docker-compose up
```