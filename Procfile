release: python manage.py migrate 
redis: redis-server  # Start the Redis server
worker: celery --app worker worker -Q tc-queue1 -l INFO -c 8
worker2: celery --app worker worker -Q tc-queue2 -l INFO -c 8
process1: python main.py
process2: python copytrade.py
process3: python trigger.py
process4: python getprice.py
process5: python trigger_price.py