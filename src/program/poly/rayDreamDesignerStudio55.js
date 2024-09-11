import {xu} from "xu";
import {Program} from "../../Program.js";

const _OUT_TYPES =
{
	quickDraw3D  : {dropdownKeys : "{TAB}{DOWN}{DOWN}{DOWN}{ENTER}", ext : ".b3d"},	// slowest but most complete
	threeDStudio : {dropdownKeys : "{TAB}{DOWN}{DOWN}{ENTER}", ext : ".3ds"},		// fails exporting some objects
	wavefrontOBJ : {dropdownKeys : "{TAB}{DOWN}{END}{UP}{ENTER}", ext : ".obj"},	// no textures
	vrml         : {dropdownKeys : "{TAB}{DOWN}{END}{ENTER}", ext : ".wrl"}			// some textures missing
};
const _OUT_TYPE_DEFAULT = "quickDraw3D";

export class rayDreamDesignerStudio55 extends Program
{
	website   = "https://archive.org/details/Ray_Dream_Studio_5.5_MetaCreations_1999";
	loc       = "win2k";
	flags   = {
		outType : `Which output file type to save as. Default: ${_OUT_TYPE_DEFAULT}`
	};
	bin       = "c:\\Program Files\\MetaCreations\\Ray Dream Studio 5.5\\rdd.exe";
	args      = r => [r.inFile()];
	osData    = r => ({
		script : `
			Sleep(4000)	; give it some time for the error windows to pop up
			Func PreOpenWindows()
				WindowFailure("", "Not the right kind of document", -1, "{ENTER}")
				WindowDismiss("Unknown Component", "", "{TAB}{TAB}{TAB}{ENTER}")
				return WinActive("Ray Dream Studio", "")
			EndFunc
			$mainWindow = CallUntil("PreOpenWindows", ${xu.SECOND*15})
			If Not $mainWindow Then
				Exit 0
			EndIf
			
			Sleep(3000)
			Send("!f")
			Send("a")
			$saveWindow = WindowRequire("Save As", "", 10)
			
			Send("${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].dropdownKeys}")
			Send("+{TAB}c:\\out\\out${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].ext}{ENTER}")
			
			WinWaitClose($saveWindow, "", 15)
			WindowDismissWait("Ray Dream Studio", "You may lose information", 10, "{ENTER}")
			WaitForStableFileSize("c:\\out\\out.3ds", ${xu.SECOND*3}, ${xu.MINUTE*5})	; can take a while, see APACHE as quickDraw3D outType
			Send("!f")
			Send("x")`
	});
	renameOut = true;
	chain     = r => `dexvert[asFormat:poly/${r.flags.outType || _OUT_TYPE_DEFAULT}]`;
}
