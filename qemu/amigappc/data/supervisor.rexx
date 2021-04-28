/* dexvert supervisor script */

ipAddress = getIPAddress()
readyFile = randFilename()
r = runAndWait('wget --quiet --output-file=NIL: "http://192.168.52.2:17735/qemuReady?osid=amigappc&ip='ipAddress'"')

inLHARemoteFile = "in/"ipAddress".lha"
inLHALocalFile = "HD:in/in.lha"
goRexxFile = "HD:in/go.rexx"
outLHALocalFile = "HD:tmp/out.lha"
outLHARemoteFile = "out/"ipAddress".lha"

DO FOREVER
	ADDRESS command DELAY 25
	r = runAndWait("DELETE HD:in HD:out ALL FORCE QUIET")
	r = runAndWait("MAKEDIR HD:in HD:out")

	r = ftpCmd("get "inLHARemoteFile" "inLHALocalFile)
	IF ~ EXISTS(inLHALocalFile) THEN ITERATE
	r = runAndWait("lha x "inLHALocalFile" HD:in/")
	ADDRESS command DELETE inLHALocalFile QUIET
	IF EXISTS(goRexxFile) THEN DO
		r = runAndWaitWithTimeout("RX "goRexxFile, 10)
		r = runAndWait("lha -r a "outLHALocalFile" HD:out/ #?")
		IF EXISTS(outLHALocalFile) THEN DO
			r = ftpCmd("put "outLHALocalFile" "outLHARemotefile)
			ADDRESS command DELETE outLHALocalFile QUIET
		DONE
	DONE
	r = ftpCmd("delete "inLHARemoteFile)
	ITERATE
END

EXIT

getIPAddress:
	PROCEDURE
	ifStatusFile = randFilename()
	r = runSavetoFile("SHOWNETSTATUS INTERFACE=RTL8029", ifStatusFile)
	ipLineFile = randFilename()
	r = runSaveToFile('GREP "Address  " 'ifStatusFile, ipLineFile)
	ipFile = randFilename()
	r = runSaveToFile('GREP -oE "192.168.52.[0-9]+" 'ipLineFile, ipFile)
	OPEN("ipFile", ipFile)
	result = READLN("ipFile")
	CLOSE("ipFile")
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
	ADDRESS command FTP
	RETURN ""

runAndWaitWithTimeout:
	PROCEDURE
	PARSE ARG cmd,maxTime
	PARSE VAR cmd progName .
	ADDRESS command RUN cmd
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
	RETURN ""

pidof:
	PROCEDURE
	PARSE ARG progName
	outFile = randFilename()
	r = runSaveToFile("Status", outFile)
	outLineFile = randFilename()
	r = runSaveToFile('grep "Loaded as command: 'progName'" 'outFile, outLineFile)
	result = runAndWait('grep -oE "[0-9]+" 'outLineFile)
	ADDRESS command DELETE outFile outLineFile QUIET
	RETURN result

runAndWait:
	PROCEDURE
	PARSE ARG cmd
	outFile = randFilename()
	r = runSaveToFile(cmd, outFile)
	OPEN("outFile", outFile)
	result = READCH("outFile", 65535)
	CLOSE("outFile")
	ADDRESS command DELETE outFile QUIET
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
	RETURN ""

randFilename: 
	RETURN "RAM:"randHex(TIME("SECONDS"), 7)

randHex:
	PROCEDURE
	PARSE ARG seed,size
	IF size=0 THEN RETURN ""
	result = RANDOM(0, 15, size + seed)
	Return D2X(result)||randHex(result, size - 1)
