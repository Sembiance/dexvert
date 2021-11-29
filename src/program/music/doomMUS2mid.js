/*
import {Program} from "../../Program.js";

export class doomMUS2mid extends Program
{
	website = "http://slade.mancubus.net/";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	runUtil = require("@sembiance/xutil").run,
	tiptoe = require("tiptoe"),
	path = require("path");

exports.meta =
{
	website : "http://slade.mancubus.net/",
	unsafe  : true
};

exports.qemu = () => "c:\\dexvert\\slade\\SLADE.exe";

exports.preArgs = (state, p, r, cb) =>	// ROB DENO: preArgs stuff can now just be done inside of args itself, since it's async now
{
	tiptoe(
		function zipInFile()
		{
			r.zipFilePath = path.join(state.cwd, "in.zip");
			runUtil.run("zip", ["-r", r.zipFilePath, state.input.base], {cwd : state.input.dirPath, silent : true}, this);
		},
		cb
	);
};

exports.args = (state, p, r) => ([r.zipFilePath]);

exports.qemuData = (state, p, r) => ({
	osid         : "winxp",
	inFilePaths  : [r.args.last()],
	script       : `
		WinWaitActive("[TITLE:SLADE; CLASS:wxWindowNR]", "", 10)
		WaitForControl("[TITLE:SLADE; CLASS:wxWindowNR]", "", "[CLASS:Button; TEXT:Entries]", ${XU.SECOND*10})
		Local $entriesPOS = ControlGetPos("[TITLE:SLADE; CLASS:wxWindowNR]", "", "[CLASS:Button; TEXT:Entries]")
		MouseClick("right", $entriesPOS[0]+26, $entriesPOS[1]+104, 1)
		Send("{UP}")
		Sleep(200)
		Send("{RIGHT}")
		Sleep(200)
		Send("{ENTER}")
		Sleep(500)
		Send("^e")

		WinWaitActive("Export Entry", "", 10)
		WaitForControl("Export Entry", "", "[CLASS:Edit; INSTANCE:1]", ${XU.SECOND*10})
		ControlSetText("Export Entry", "", "[CLASS:Edit; INSTANCE:1]", "c:\\out\\out.mid")

		Sleep(200)
		ControlClick("Export Entry", "", "[CLASS:Button; TEXT:&Save]")

		WinWaitClose("Export Entry", "", 10)

		Send("!f")
		Sleep(200)
		Send("x")

		WinWaitActive("Unsaved Changes", "", 10)
		WaitForControl("Unsaved Changes", "", "[CLASS:Button; TEXT:&No]", ${XU.SECOND*10})
		ControlClick("Unsaved Changes", "", "[CLASS:Button; TEXT:&No]")

		WinWaitClose("[TITLE:SLADE; CLASS:wxWindowNR]", "", 100)
		
		WaitForPID(ProcessExists("SLADE.exe"), ${XU.MINUTE*5})`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.mid"), path.join(state.output.absolute, `${state.input.name}.mid`))(state, p, cb);
*/
