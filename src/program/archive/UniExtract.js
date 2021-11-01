"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://www.legroom.net/software/uniextract",
	flags :
	{
		uniExtractType : `Which type of extraction to choose. Examples: "i3comp extraction" or "STIX extraction"`
	}
};

exports.qemu = () => "c:\\dexvert\\uniextract161\\UniExtract.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.args[0], ...(state.extraFilenames || [])],
	script : `
		Local $mainWindow = WinWaitActive("Universal Extractor", "", 10)

		ControlSetText("Universal Extractor", "", "[CLASS:Edit; INSTANCE:2]", "c:\\out\\")
		Sleep(200)

		ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:&OK]")

		WinWaitClose($mainWindow, "", 10)

		Local $decisionWindow = WinWaitActive("Universal Extractor", "", 10)
		If $decisionWindow Then
			${r.flags.uniExtractType ? `ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:${r.flags.uniExtractType}]")` : ""}
			ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:&OK]")
		EndIf

		Local $hasError = WinWaitActive("Universal Extractor", "could not be extracted", 5)
		If $hasError Then
			ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:&Cancel]")
		EndIf

		WinWaitClose("Universal Extractor", "", 10)

		ProcessWaitClose("UniExtract.exe", 10)`
});
