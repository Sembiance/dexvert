/*
import {Program} from "../../Program.js";

export class pabloDraw extends Program
{
	website = "http://picoe.ca/products/pablodraw/";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://picoe.ca/products/pablodraw/",
	unsafe  : true
};

exports.qemu = () => "C:\\Documents and Settings\\dexvert\\Local Settings\\Apps\\2.0\\XN7ZX61H.J6Q\\O72LB2O7.1KE\\pabl..tion_29b20c6ea23027e7_0003.0002_55cb9279e07d9803\\PabloDraw.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	osid        : "winxp",
	inFilePaths : [r.args[0]],
	script      : `
		$mainWindowVisible = WinWaitActive("[REGEXPTITLE:(PabloDraw.*)]", "", 10)
		If $mainWindowVisible Not = 0 Then
			Sleep(2000)
			
			; Disable animation which will cause it to finish drawing instantly, maybe?
			Send("!v")
			Send("a");
			Send("e");

			Sleep(2000)

			; Issue save command
			Send("^+s")

			Sleep(500)

			$saveVisible = WinWaitActive("[TITLE:Specify the file to save]", "", 10)
			If $saveVisible Not = 0 Then
				ControlSetText("Specify the file to save", "", "[CLASS:Edit; INSTANCE:1]", "c:\\out\\outfile.png")
				Sleep(200)
				ControlClick("Specify the file to save", "", "[CLASS:Button; TEXT:&Save]")
			EndIf

			Sleep(200)
			Send("!x")
		EndIf`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
*/
