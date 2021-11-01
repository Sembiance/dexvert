"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website : "https://www.buraks.com/swifty/xena.html",
	unsafe  : true
};

exports.qemu = () => "dirOpener300-850-1-PC.exe";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.absolute) => { r.inPath = inPath; r.outPath = outPath; return []; };
exports.qemuData = (state, p, r) => ({
	osid         : "winxp",
	inFilePaths  : [r.inPath],
	outDirPath   : r.outPath,
	dontMaximize : true,
	script       : `
		WinWaitActive("dirOpener300-850-1-PC", "", 10)

		; Sometimes dirOpener refuses to save the file to c:\\out and sticks it in C:\\ instead. Sigh.
		$badProjectOutputPath = "c:\\outdirOpened output of in.dir"
		$badCastOutputPath = "c:\\outdirOpened output of in.cst"

		; Check to see if previous leftover files exist, if so delete em
		If FileExists($badProjectOutputPath) Then
			FileDelete($badProjectOutputPath)
		EndIf

		If FileExists($badCastOutputPath) Then
			FileDelete($badCastOutputPath)
		EndIf

		; Sometimes dirOpener chooses to forget all it's preferences, especially the 'Exit After Converting'
		; So we click over to the Preferences tab, reset and then set all the settings the way we want
		Sleep(100)
		MouseClick("left", 321, 221)
		Sleep(100)
		MouseClick("left", 379, 435)
		Sleep(100)
		MouseClick("left", 235, 267)
		Sleep(100)
		MouseClick("left", 236, 309)
		Sleep(100)
		MouseClick("left", 236, 399)
		Sleep(100)
		
		;MouseClick("left", 620, 401)
		;WinWaitActive("Browse for Folder", "", 10)
		;Send("{DOWN}{RIGHT}o{ENTER}")
		;Sleep(500)

		MouseClick("left", 404, 398)
		Sleep(100)
		Send("+{HOME}c:\\out")
		Sleep(100)
		
		MouseClick("left", 469, 434)
		Sleep(1000)

		; Now click Open and being
		MouseClick("left", 255, 440)

		WinWaitActive("[TITLE:Select file(s) to open]", "", 10)

		Sleep(200)
		Send("c:\\in\\${path.basename(r.inPath)}{ENTER}")
		Sleep(200)

		; Some are missing files and ask "Where is" something
		; Some times errors show up about scripts or other director errors
		; Some files show custom alerts that pop up (pc.dir) some have several in a row
		; They all are the same window class though, so we just use this loop
		Local $alertWindow
		Do
			$alertWindow = WinWaitActive("[CLASS:#32770]", "", 5)
			If $alertWindow Not = 0 Then
				ControlClick("[CLASS:#32770]", "", "[CLASS:Button; TEXT:OK]")
				ControlClick("[CLASS:#32770]", "", "[CLASS:Button; TEXT:&Yes]")
				ControlClick("[CLASS:#32770]", "", "[CLASS:Button; TEXT:Cancel]")
			EndIf
		Until $alertWindow = 0

		WaitForPID(ProcessExists("dirOpener300-850-1-PC.exe"), ${XU.MINUTE*2})

		Sleep(1000)

		; See if it copied to the wrong output and if so, copy it over to c:\\out
		If FileExists($badProjectOutputPath) Then
			FileMove($badProjectOutputPath, "c:\\out\\dexvert.dir")
		EndIf

		If FileExists($badCastOutputPath) Then
			FileMove($badCastOutputPath, "c:\\out\\dexvert.cst")
		EndIf`
});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputFiles()
		{
			fileUtil.glob(r.outPath, "*", {nodir : true}, this);
		},
		function renameOutputFile(outputFilePaths)
		{
			if(!outputFilePaths || outputFilePaths.length===0)
				return this();
			
			if(outputFilePaths.length>1 && state.verbose)
				XU.log`dirOpener produced more than 1 file, this is unexpected and unsupported: [${outputFilePaths.join("] [")}`;

			// If the output is exactly this big, then the conversion didn't produce anything
			if(fs.statSync(outputFilePaths[0]).size===263100)
				fileUtil.unlink(outputFilePaths[0], this);
			else
				fileUtil.move(outputFilePaths[0], path.join(r.outPath, `${state.input.name}${path.extname(outputFilePaths[0])}`), this);
		},
		cb
	);
};
