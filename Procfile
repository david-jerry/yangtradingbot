release: python manage.py migrate 
worker: celery --app worker worker -Q tc-queue1 -l INFO -c 8
process1: python main.py
process2: python copytrade.py
process3: python trigger.py