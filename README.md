# yangtradingbot
#Copy trade
in root: 1 line is 1 terminal
celery --app worker worker -Q tc-queue1 -l INFO -c 4 #run the worker
python3 copytrade.py #run the copytrade listener
python3 trigger.py #run the customer listener
python3 test.py #run the unit test as a copytrade do transaction buy sell on uniswap
#############################################

