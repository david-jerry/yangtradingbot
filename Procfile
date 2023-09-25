release: python manage.py migrate 
worker: celery --app worker worker -Q tc-queue -l INFO -c 4
process1: python main.py
process2: python copytrade.py
process3: python trigger.py