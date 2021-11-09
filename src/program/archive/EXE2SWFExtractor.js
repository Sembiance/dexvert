/*
import {Program} from "../../Program.js";

export class EXE2SWFExtractor extends Program
{
	website = "https://sothink.com/product/flashdecompiler/";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	path = require("path");

exports.meta =
{
	website : "https://sothink.com/product/flashdecompiler/",
	unsafe  : true
};

exports.qemu = () => "EXE2SWFExtractor.exe";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.absolute) => { r.outPath = outPath; return [inPath]; };
exports.qemuData = (state, p, r) => ({
	osid         : "winxp",
	inFilePaths  : [r.args[0]],
	script       : `
		WinWaitActive("Sothink EXE to SWF Extractor", "", 10)

		Sleep(250)

		ControlSetText("Sothink EXE to SWF Extractor", "", "[CLASS:Edit; INSTANCE:1]", "c:\\out")

		ControlClick("Sothink EXE to SWF Extractor", "", "[CLASS:Button; TEXT:Extract]")

		WaitForControl("Sothink EXE to SWF Extractor", "", "[CLASS:Button; TEXT:OK]", ${XU.SECOND*20})

		ControlClick("Sothink EXE to SWF Extractor", "", "[CLASS:Button; TEXT:OK]")

		ProcessClose("EXE2SWFExtractor.exe")

		WaitForPID(ProcessExists("EXE2SWFExtractor.exe"), ${XU.SECOND*10})`
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
				XU.log`EXE2SWFExtractor produced more than 1 file, this is unexpected and unsupported: [${outputFilePaths.join("] [")}`;

			XU.log`outputFilePaths[0] ${outputFilePaths[0]}`;
			fileUtil.move(outputFilePaths[0], path.join(r.outPath, `${state.input.name}${path.extname(outputFilePaths[0])}`), this);
		},
		cb
	);
};
*/
