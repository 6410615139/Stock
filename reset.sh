rm -rf db.sqlite3

python manage.py makemigrations
python manage.py migrate
python manage.py init_branch_list
python manage.py createsuperuser