# Capture a native stack at glibc's abort in the running game, then kill it (it is already aborting).
#
# Attach non-batch, with input held open (batch mode and a closing stdin both end the session
# early), and resolve libraries inside the Steam Runtime container:
#
#   { printf 'set sysroot /proc/%s/root\nfile /proc/%s/exe\n' PID PID; cat catch-abort.gdb; sleep 86400; } \
#     | gdb -q -nx -p PID > capture.txt 2>&1
#
# Wine raises and handles SEGV, ILL, BUS, FPE, TRAP and USR1/2 itself, so they pass silently.
# The capture runs as the catchpoint's commands: anything queued on gdb's input would run while
# the game is still going. An error inside a command list abandons the rest of it, so the raw
# stack read, which ends in unmapped memory, is wrapped in Python.
set pagination off
set confirm off
set debuginfod enabled off
set print thread-events off
handle SIGSEGV nostop noprint pass
handle SIGILL nostop noprint pass
handle SIGBUS nostop noprint pass
handle SIGFPE nostop noprint pass
handle SIGTRAP nostop noprint pass
handle SIGUSR1 nostop noprint pass
handle SIGUSR2 nostop noprint pass
handle SIGQUIT nostop noprint pass
handle SIGPIPE nostop noprint pass
handle SIGCHLD nostop noprint pass
handle SIGALRM nostop noprint pass
catch signal SIGABRT
commands
  echo \n=== STOPPED ===\n
  bt 80
  echo \n=== registers ===\n
  info registers
  echo \n=== all threads ===\n
  thread apply all bt 30
  echo \n=== libraries ===\n
  info sharedlibrary
  echo \n=== raw stack ===\n
  python
try:
    gdb.execute("x/8192wx $sp")
except gdb.error as e:
    print("raw stack ends:", e)
  end
  echo \n=== DONE ===\n
  kill
  quit
end
echo === attached, continuing ===\n
continue
