#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py seed_objetivos
python manage.py seed_estudos
python manage.py seed_anotacoes
python manage.py seed_projetos
python manage.py seed_competencias
python manage.py seed_revisoes
python manage.py seed_certificacoes
