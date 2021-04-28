"use strict";
const XU = require("@sembiance/xu"),
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

		ControlClick("Select output options", "", "[CLASS:Button; TEXT:Finish]")`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "in.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
