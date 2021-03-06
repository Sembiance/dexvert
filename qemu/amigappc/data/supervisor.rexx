/* dexvert supervisor script */
debugMode = 1
myPid = readFile("RAM:supervisor.pid")

ipAddress = getIPAddress()
r = runAndWait('wget --quiet --output-file=NIL: "http://192.168.52.2:17735/qemuReady?osid=amigappc&ip='ipAddress'"')

inLHARemoteFile = "in/"ipAddress".lha"
inLHALocalFile = "HD:tmp/in.lha"
goRexxFile = "HD:in/go.rexx"
outLHALocalFile = "HD:tmp/out.lha"
outLHARemoteFile = "out/"ipAddress".lha"

DO FOREVER
	dbg("Cleaning up in/out")
	ADDRESS command "DELETE HD:in HD:out HD:tmp ALL FORCE QUIET"
	ADDRESS command "MAKEDIR HD:in HD:out HD:tmp"

	dbg("Waiting for remote in.lha and go.rexx")
	r = waitForGoRexx()
	
	dbg("Running go.rexx")
	ADDRESS command DELAY 25
	r = runAndWaitWithTimeout("RX "goRexxFile, 300.0)
	
	dbg("Creating out.lha")
	r = runAndWait("lha -r -a -q a "outLHALocalFile" HD:out/ #?")
	IF EXISTS(outLHALocalFile) THEN DO
		dbg("Uploading out.lha")
		r = ftpCmd("put "outLHALocalFile" "outLHARemotefile)
		ADDRESS command DELETE outLHALocalFile FORCE QUIET
	END

	dbg("Deleting remote in.lha")
	r = ftpCmd("delete "inLHARemoteFile)
END

EXIT

dbg:
	PROCEDURE EXPOSE debugMode
	PARSE ARG msg
	IF debugMode=1 THEN ECHO msg
	RETURN 0

waitForGoRexx:
	PROCEDURE EXPOSE inLHARemoteFile inLHALocalFile goRexxFile debugMode
	DO FOREVER
		ADDRESS command DELAY 25
		r = ftpCmd("get "inLHARemoteFile" "inLHALocalFile)
		IF ~ EXISTS(inLHALocalFile) THEN ITERATE
		dbg("Found and extracting in.lha file")
		ADDRESS command
		LHA "-q x "inLHALocalFile" HD:in/"
		DELETE inLHALocalFile
		ADDRESS
		IF EXISTS(goRexxFile) THEN LEAVE
		ELSE dbg("ERROR: The in.lha file failed to produce: "goRexxFile)
	END
	RETURN 0

getIPAddress:
	PROCEDURE
	ifStatusFile = randFilename()
	ipLineFile = randFilename()
	ipFile = randFilename()
	ADDRESS command SHOWNETSTATUS "INTERFACE=RTL8029" ">"ifStatusFile
	ADDRESS command GREP '"Address  "' ifStatusFile ">"ipLineFile
	ADDRESS command GREP "-oE" "192.168.52.[0-9]+" ipLineFile ">"ipFile
	result = readFile(ipFile)
	ADDRESS command DELETE ifStatusFile ipLineFile ipFile QUIET
	RETURN result

ftpCmd:
	PROCEDURE
	PARSE ARG cmd
	QUEUE "open 192.168.52.2 7021"
	QUEUE "anonymous"
	QUEUE "passive"
	QUEUE cmd
	QUEUE "quit"
	ADDRESS command FTP ">NIL:"
	RETURN 0

runAndWaitWithTimeout:
	PROCEDURE EXPOSE myPid
	PARSE ARG cmd,maxTime
	PARSE VAR cmd progName .
	ADDRESS command RUN ">NIL:" cmd
	startAt = TIME("ELAPSED")
	DO FOREVER
		pid = pidof(progName)
		IF pid="" THEN LEAVE
		IF (TIME("ELAPSED") - startAt) >= maxTime THEN DO
			ECHO "Command ("cmd") took too long. Breaking..."
			ADDRESS command BREAK pid
			LEAVE
		END
	END
	RETURN 0

pidof:
	PROCEDURE EXPOSE myPid
	PARSE ARG progName
	outFile = randFilename()
	outAllMatchesFile = randFilename()
	outSomeMatchesFile = randFilename()
	outMatchFile = randFilename()
	r = RunSaveToFile("STATUS", outFile)
	r = RunSaveToFile('GREP "Loaded as command: 'progName'" 'outFile, outAllMatchesFile)
	r = RunSaveToFile('GREP -vE "Process[ ]+'myPid'" 'outAllMatchesFile, outSomeMatchesFile)
	r = RunSavetoFile("TAIL -1l "outSomeMatchesFile, outMatchFile)
	result = runAndWait('GREP -oE "[0-9]+" 'outMatchFile)
	ADDRESS command DELETE outFile outAllMatchesFile outSomeMatchesFile outMatchFile FORCE QUIET
	RETURN result

runAndWait:
	PROCEDURE
	PARSE ARG cmd
	outFile = randFilename()
	r = runSaveToFile(cmd, outFile)
	result = readFile(outFile)
	ADDRESS command DELETE outFile QUIET
	RETURN result

readFile:
	PROCEDURE
	PARSE ARG inFile
	OPEN("inFile", inFile)
	IF LINES("inFile")<=1 THEN result = READLN("inFile")
	ELSE result = READCH("inFile", 65535)
	CLOSE("inFile")
	RETURN result

runSaveToFile:
	PROCEDURE
	PARSE ARG cmd,outFile
	scriptFile = randFilename()
	OPEN("scriptFile", scriptFile, WRITE)
	WRITELN("scriptFile", cmd" > "outFile)
	CLOSE("scriptFile")
	ADDRESS command EXECUTE scriptFile
	ADDRESS command DELETE scriptFile QUIET
	RETURN 0

randFilename: 
	RETURN "RAM:"randHex(TIME("SECONDS"), 7)

randHex:
	PROCEDURE
	PARSE ARG seed,size
	IF size=0 THEN RETURN 0
	result = RANDOM(0, 15, size + seed)
	Return D2X(result)||randHex(result, size - 1)
