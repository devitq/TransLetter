sort-requirements requirements/dev.txt
sort-requirements requirements/prod.txt
sort-requirements requirements/test.txt
sort-requirements requirements/lints.txt
cd transletter
black .
flake8 .
djlint . --reformat --format-css --format-js
python manage.py makemigrations --check --dry-run
python manage.py test