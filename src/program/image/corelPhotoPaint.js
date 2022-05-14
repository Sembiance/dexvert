import {xu} from "xu";
import {Program} from "../../Program.js";

export class corelPhotoPaint extends Program
{
	website  = "https://archive.org/details/Corel_Photo-Paint_8_-_Win95_Eng";
	loc      = "winxp";
	bin      = "c:\\Corel\\Photo-Paint8\\Programs\\photopnt.exe";
	flags   = {
		outType : "Which format to output. png usually works and is the default, but sometimes png isn't available, then use tiff"
	};
	bruteFlags = { poly : {}, video : {} };
	args     = r => [r.inFile()];
	qemuData = r => ({
		alsoKill : ["cdrconv.exe"],
		script : `
		$mainWindow = WindowRequire("Corel PHOTO-PAINT 8", "", 5)
		WindowFailure("Corel PHOTO-PAINT - Error", "", 2, "{ENTER}")
		
		Func PreOpenWindows()
			WindowDismiss("Import Into Bitmap", "", "{ENTER}")
			WindowDismiss("Import 3D Model", "", "{ENTER}")
			WindowDismiss("Import FlashPix Image Properties", "", "{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{ENTER}")
			WindowDismiss("Font Matching Results", "", "{ENTER}")
			WindowDismiss("HPGL Options", "", "{ENTER}")
			WindowDismiss("Partial Load Movie", "", "{ENTER}")
		EndFunc
		CallUntil("PreOpenWindows", ${xu.SECOND*3})
		
		WindowFailure("Corel PHOTO-PAINT - Error", "", 1, "{ENTER}")
		WindowFailure("[CLASS:#32770]", "Error Reading", 1, "{ENTER}")

		WinMenuSelectItem($mainWindow, "", "&File", "&Export...")
		$exportWindow = WindowRequire("Export an Image to Disk", "", 5)
		Send("c:\\out\\out.${r.flags.outType || "png"}{TAB}{RIGHT}{HOME}${r.flags.outType==="avi" ? "vv" : (r.flags.outType || "png").charAt(0).repeat(2)}{ENTER}{ENTER}")
		WinWaitClose($exportWindow, "", 5)

		Func PostExportWindows()
			WindowDismiss("Corel PHOTO-PAINT - Warning", "", "{ENTER}")
			return WindowDismiss("PNG Options", "", "{ENTER}")
		EndFunc
		CallUntil("PostExportWindows", ${xu.SECOND*3})
		
		WinWaitActive($mainWindow, "", 3)
		WinMenuSelectItem($mainWindow, "", "&File", "E&xit")
		WindowDismissWait("Corel PHOTO-PAINT 8", "Save changes to", 1, "n")`
	});
	renameOut  = true;
	chain      = r => `?dexvert[asFormat:${r.flags.outType==="avi" ? "video/avi" : `image/${r.flags.outType}`}]`;
	chainCheck = r => ["tiff", "avi"].includes(r.flags.outType);
}
