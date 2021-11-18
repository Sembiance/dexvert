import {Program} from "../../Program.js";
import {path} from "std";

export class graphicWorkshopProfessional extends Program
{
	website  = "http://www.mindworkshop.com/gwspro.html";
	loc      = "win2k";
	bin      = "c:\\GraphicWorkshopProfessional\\GWSPRO.EXE"
	args     = r => [r.inFile()]
	qemuData = () => ({
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
	post = async r => await r.f.remove("new", path.join(r.f.outDir.absolute, "out.THN"), {unlink : "true"})
}
