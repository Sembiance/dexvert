/*
import {Program} from "../../Program.js";

export class graphicWorkshopProfessional extends Program
{
	website = "http://www.mindworkshop.com/gwspro.html";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path");

exports.meta =
{
	website : "http://www.mindworkshop.com/gwspro.html"
};

exports.qemu = () => "c:\\GraphicWorkshopProfessional\\GWSPRO.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.args[0], ...(state.extraFilenames || [])],
	script : `
		$mainWindowVisible = WinWaitActive("[CLASS:GraphicWorkshopProfessionalPicture]", "", 7)
		If $mainWindowVisible = 0 Then
			$errorVisible = WinWaitActive("[TITLE:Message]", "", 7)
			If $errorVisible Not = 0 Then
				ControlClick("[TITLE:Message]", "", "[CLASS:Button; TEXT:Ok]")
				ControlClick("[TITLE:Message]", "", "[CLASS:Button; TEXT:No]")

				Sleep(1500)

				ControlClick("[TITLE:Message]", "", "[CLASS:Button; TEXT:Ok]")
				ControlClick("[TITLE:Message]", "", "[CLASS:Button; TEXT:No]")
			EndIf
		Else
			Sleep(1000)
			Send("!p")
			Sleep(100)
			Send("a")
			Sleep(100)

			$exportVisible = WinWaitActive("[TITLE:Destination]", "", 5)
			If $exportVisible Not = 0 Then
				ControlClick("[TITLE:Destination]", "", "[CLASS:Button; TEXT:PNG]")

				WinWaitActive("[TITLE:Save To]", "", 30)
				ControlClick("[TITLE:Save To]", "", "[CLASS:Edit]")

				Send("{HOME}{SHIFTDOWN}{END}{SHIFTUP}{BACKSPACE}c:\\out\\out.png")
				ControlClick("[TITLE:Save To]", "", "[CLASS:Button; TEXT:&Save]")

				WinWaitActive("[CLASS:GraphicWorkshopProfessionalPicture]", "", 30)
				Sleep(200)
			EndIf

			WinClose("[CLASS:GraphicWorkshopProfessionalPicture]")
		EndIf
		
		Sleep(200)
		ControlClick("[TITLE:Program Error]", "", "[CLASS:Button; TEXT:OK]")
		
		Sleep(1000)`
});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function moveOutAndDeleteThumb()
		{
			p.util.file.unlink(path.join(state.output.absolute, "out.THN"))(state, p, this.parallel());
			p.util.file.move(path.join(state.output.absolute, "out.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, this.parallel());
		},
		cb
	);
};
*/
