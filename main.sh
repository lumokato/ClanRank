ps -ef |grep main.py |awk '{print $2}'|xargs kill -9
nohup python3 main.py &
