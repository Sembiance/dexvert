import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class graphicWorkshopProfessional extends Program
{
	website  = "http://www.mindworkshop.com/gwspro.html";
	loc      = "win2k";
	bin      = "c:\\GraphicWorkshopProfessional\\GWSPRO.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			Func MainWindowOrFailure()
				WindowFailure("[TITLE:Message]", "Error opening file", -1, "{ESCAPE}")
				WindowFailure("[TITLE:Message]", "Corrupted file", -1, "{ESCAPE}")

				; Program can't save convert an animated gif, sigh, such as image/macPageMillGIF/MURPH.GIF
				WindowFailure("[CLASS:GraphicWorkshopProfessionalAnimateGIF]", "", -1, "{ESCAPE}")

				return WinActive("[CLASS:GraphicWorkshopProfessionalPicture]", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*10})

			Sleep(1000)
			SendSlow("!pa")

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
			
			Sleep(1000)

			KillAll("GWSPRO.EXE")

			SendSlow("{ESCAPE}{ESCAPE}{ESCAPE}{ESCAPE}{ESCAPE}")`
	});
	post      = async r => await r.f.remove("new", path.join(r.f.outDir.absolute, "out.THN"), {unlink : "true"});
	renameOut = true;
}
