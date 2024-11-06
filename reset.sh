ps -ef |grep app.py |awk '{print $2}'|xargs kill -9
ps -ef |grep main.py |awk '{print $2}'|xargs kill -9
ps -ef |grep api.py |awk '{print $2}'|xargs kill -9
nohup python3 app.py &
nohup python3 main.py &
nohup python3 api.py &
