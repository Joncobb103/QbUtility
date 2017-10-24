$pid = $1
echo ${pid}
pkill -9 python
sh runday.sh