ps -ef |grep http.server |awk '{print $2}'|xargs kill -9
ps -ef |grep main.py |awk '{print $2}'|xargs kill -9
ps -ef |grep api |awk '{print $2}'|xargs kill -9
nohup python3 -m http.server &
nohup python3 main.py &
nohup python3 api.py &
