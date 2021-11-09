/*
import {Program} from "../../Program.js";

export class awaveStudio extends Program
{
	website = "https://archive.org/details/awave70_zip";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website : "https://archive.org/details/awave70_zip"
};

exports.qemu = () => "c:\\Program Files\\Awave Studio\\Awave.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => { r.inPath = inPath; return ["-BATCH"]; };
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.inPath],
	script : `
		WinWaitActive("Select conversion type", "", 10)
		ControlClick("Select conversion type", "", "[CLASS:Button; TEXT:&Next >]")

		WinWaitActive("Select input files", "", 10)
		ControlClick("Select input files", "", "[CLASS:Button; TEXT:Add...]")

		WinWaitActive("Open new file", "", 10)

		Sleep(200)
		Send("c:\\in\\${path.basename(r.inPath)}{ENTER}")
		Sleep(200)

		WinActivate("Select input files", "");
		WinWaitActive("Select input files", "", 10)
		ControlClick("Select input files", "", "[CLASS:Button; TEXT:&Next >]")

		WinWaitActive("Select output options", "", 10)

		Local $formatWAV = ControlCommand("Select output options", "", "[CLASS:ComboBox; INSTANCE:2]", "FindString", ".wav - Microsoft Wave file")
		ControlCommand("Select output options", "", "[CLASS:ComboBox; INSTANCE:2]", "SetCurrentSelection", $formatWAV)

		ControlSetText("Select output options", "", "[CLASS:Edit; INSTANCE:2]", "c:\\out")

		ControlClick("Select output options", "", "[CLASS:Button; TEXT:Finish]")
		
		WaitForPID(ProcessExists("Awave.exe"), ${XU.MINUTE*5})`
});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputFiles()
		{
			fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
		},
		function renameOutputFiles(outputFilePaths)
		{
			outputFilePaths.parallelForEach((outputFilePath, subcb) =>
			{
				const part = ["in - in", "in"].find(v => path.basename(outputFilePath).includes(v));
				if(!part)
					return setImmediate(subcb);
				
				fs.rename(outputFilePath, path.join(path.dirname(outputFilePath), path.basename(outputFilePath).replaceAll(part, state.input.name)), subcb);
			}, this);
		},
		cb
	);
};
*/
