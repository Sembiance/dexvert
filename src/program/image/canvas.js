import {xu} from "xu";
import {Program} from "../../Program.js";

export class canvas extends Program
{
	website  = "http://fileformats.archiveteam.org/wiki/Canvas";
	loc      = "winxp";
	bin      = "c:\\Program Files\\ACD Systems\\Canvas 14\\Canvas14.exe";
	flags   = {
		nonRaster : "Set this to true and the raster enforcement check will be skipped. Warning, this can result in garbage output."
	};
	args     = r => [r.inFile()];
	qemuData = r => ({
		alsoKill : ["CanvasInTouch2.exe"],
		script   : `
		AutoItSetOption("PixelCoordMode", 0)
		AutoItSetOption("SendKeyDelay", 20)

		$mainWindow = WindowRequire("Canvas 14", "", 5)

		Func PreOpenWindows()
			WindowFailure("Canvas Alert", "Error loading document", -1, "{ENTER}")
			WindowFailure("DWGdirect Exception", "", -1, "{ENTER}")
			WindowDismiss("Canvas", "Register Canvas to finish", "{ENTER}")
			WindowDismiss("Canvas - Registration", "", "{ESCAPE}")
			WindowDismiss("Choose Resolution", "", "{ENTER}")
			WindowDismiss("CGM/CGM Import Options", "", "{ENTER}")
			WindowDismiss("DICOM Import Options", "", "{ENTER}")
			WindowDismiss("DWG & DXF Import", "", "{ENTER}")
			WindowDismiss("EPSF Import Options", "", "+{TAB}{DOWN}{ENTER}")
			WindowDismiss("PDF & PS Import", "", "{ENTER}")
			WindowDismiss("Photoshop Import", "", "+{TAB}{DOWN}{DOWN}{ENTER}")
			WindowDismiss("Open Images", "", "{TAB}1{ENTER}")
			WindowDismiss("Select Layout", "", "{ENTER}")
		EndFunc
		CallUntil("PreOpenWindows", ${xu.SECOND*4})

		${!r.flags?.nonRaster ? `
			; check to ensure the file was rendered as a raster image
			; some files like cdr/WI.CDR will open as 'text/hex'. In fact canvas will open any text file and just render the text
			; couldn't find a way to prevent it and the only way to detect is if we have more than 1 page/layer/object
			; I'd love to check this directly with a text check byut 
			; so I have to resort to using a PxelChecksum. Not sure how fragile this is or not
			Send("!fi")
			$propWindow = WindowRequire("Document Properties", "", 5)
			Send("+{TAB}+{TAB}+{TAB}{HOME}{RIGHT}")

			Sleep(1000)
			
			Local $propsCheckSum = PixelChecksum(115, 247, 142, 305, 1, $propWindow)
			Send("{ESCAPE}")

			If $propsCheckSum <> 1942773917 Then
				Send("!x")
				Exit 1
			EndIf` : ""}

		Send("^+s")

		$exportWindow = WindowRequire("Save As", "", 5)
		Send("c:\\out\\out.png{TAB}{DOWN}{END}${"{UP}".repeat(14)}{ENTER}{ENTER}")
		WinWaitClose($exportWindow, "", 5)
		
		Func PostExportWindows()
			WindowFailure("PDF Options", "", -1, "{ESCAPE}")
			WindowDismiss("Render Image", "", "{ENTER}")
			WindowDismiss("Canvas Message", "Would you like to associate the current document with the new file", "n")
		EndFunc
		CallUntil("PostExportWindows", ${xu.SECOND*2})

		WinWaitActive($mainWindow, "", 3)
		Send("!x")
		WindowDismissWait("Canvas Message", "Do you want to save", 2, "n")`
	});
	renameOut  = true;
}
