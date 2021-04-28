/* backs up files to remote FTP */
QUEUE "open 192.168.52.2 7021"
QUEUE "anonymous"
QUEUE "passive"
QUEUE "put HD:dexvert/supervisor.rexx backup/supervisor.rexx"
QUEUE "put HD:dexvert/launchSupervisor.script backup/launchSupervisor.script"
QUEUE "put HD:dexvert/backup.rexx backup/backup.rexx"
QUEUE "put S:Network-Startup backup/Network-Startup"
QUEUE "quit"
ADDRESS command FTP
