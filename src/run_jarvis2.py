# This is a nanny script to run Jarvis2 and also responsible for its termination

import sys, getopt, os, subprocess, psutil
from logger import logger

# Absolute path
abs_path = os.path.dirname(os.path.abspath('__file__'))

# File where we'll store the PID
pid_file_path = abs_path + "/../data/jarvis2.pid"

def usage(errno):
    print "Use '-d' option to run server -OR- '-s' option to terminate"
    print "Example:"
    print "1. python run_jarvis2.py -d [local | stage | prod]"
    print "2. python run_jarvis2.py -s <signal_number>"
    sys.exit(errno)

def parse(argv):
    deployment = ''
    signal = ''
    try:
      opts, args = getopt.getopt(argv,"hd:s:",["deploy=","signal="])
    except getopt.GetoptError:
      usage(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(0)
        elif opt in ("-d", "--deploy"):
            deployment = arg
        elif opt in ("-s", "--signal"):
            signal = arg

    if deployment and signal:
        usage(1)
    elif deployment:
        run(deployment)
    elif signal:
        terminate(int(signal))

def check_process(pid):
    ret = False
    if pid == '':
        return ret
    for p in psutil.process_iter():
        try:
            if int(p.pid) == int(pid):
                ret = True
                break
        except psutil.Error:
            pass
    return ret

def run(deployment):
    pid = read_pid()
    if check_process(pid):
            logger.info("Jarvis2 already started. Exiting!")
    else:
        py_cmd = abs_path + "/XmppJarvis2Bot.py"
        process = subprocess.Popen(['nohup', 'python', py_cmd, deployment],
                 stdout=open('logfile.out', 'w'),
                 stderr=open('logfile.err', 'a'),
                 preexec_fn=os.setpgrp)
        logger.info("Starting Jarvis2 with process ID: " + str(process.pid))
        write_pid(process.pid)

def terminate(signal):
    pid = read_pid()
    if check_process(pid):
        logger.info("Terminating Jarvis2 running with process ID: " + str(pid))
        os.kill(int(pid), signal)
        write_pid(-1)
    else:
        logger.info("Jarvis2 is not running. Exiting!")

def write_pid(pid):
    pidfile = open(pid_file_path, 'w')
    pidfile.write(str(pid))
    pidfile.close()

def read_pid():
    pidfile = open(pid_file_path, 'r')
    pid = pidfile.read()
    pidfile.close()
    return pid

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage(1)
    parse(sys.argv[1:])