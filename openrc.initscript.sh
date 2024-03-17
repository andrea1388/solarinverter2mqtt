#!/sbin/openrc-run

command="python3 inv2mqtt.py"
command_args=""
name=$RC_SVCNAME
pidfile="/run/$RC_SVCNAME.pid"
command_background="yes"
output_logger="/usr/bin/logger"
error_logger="/usr/bin/logger"

depend() {
        need net
        use logger
}

start_pre() {
    cd /root/solarinverter2mqtt
}