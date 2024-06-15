import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

const _INTERMEDIATE_FORMATS =
{
	threeDStudio   : {x : 240, y : 257, ext : ".3ds"},
	direct3DObject : {x : 239, y : 294, ext : ".x"  },
	quickDraw3D    : {x : 240, y : 328, ext : ".3dm"},
	shockwave3D    : {x : 246, y : 351, ext : ".w3d"},
	stl            : {x : 226, y : 372, ext : ".stl"},
	wavefrontOBJ   : {x : 236, y : 441, ext : ".obj"}
};
const _DEFAULT_INTERMEDIATE = "wavefrontOBJ";

export class cinema4D82 extends Program
{
	website = "https://archive.org/details/twilight-dvd087";
	loc     = "winxp";
	bin     = "c:\\Program Files\\Maxon Cinema 4D 8.2\\CINEMA_4D.exe";
	flags   = {
		outType : `Which intermediate format to output. Default: ${_DEFAULT_INTERMEDIATE}`
	};
	args    = r => [r.inFile()];
	osData  = r => ({
		script : `
			Func MainWindowOrFailure()
				WindowFailure("CINEMA 4D", "Unknown file format!", -1, "{ESCAPE}")
				return WinActive("CINEMA 4D - [${path.basename(r.inFile())}]", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*30})
			If Not $mainWindow Then
				Exit 0
			EndIf
			
			Sleep(7000)	; big models like daylight.c4d take a while to load but haven't found a way to detect when it's done loading
			MouseClick("left", 16, 29, 1, 10)
			MouseClick("left", 40, 252, 1, 10)
			MouseMove(233, 251, 13)
			MouseClick("left", ${_INTERMEDIATE_FORMATS[r.flags.outType || _DEFAULT_INTERMEDIATE].x}, ${_INTERMEDIATE_FORMATS[r.flags.outType || _DEFAULT_INTERMEDIATE].y}, 1, 10)

			$saveWindow = WindowRequire("Save File", "", 10)
			Send("c:\\out\\out${_INTERMEDIATE_FORMATS[r.flags.outType || _DEFAULT_INTERMEDIATE].ext}{ENTER}")
			WinWaitClose($saveWindow, "", 30)
			WaitForStableFileSize("c:\\out\\out${_INTERMEDIATE_FORMATS[r.flags.outType || _DEFAULT_INTERMEDIATE].ext}", ${xu.SECOND*10}, ${xu.MINUTE*2})` });	// huge models like daylight.c4d take a long time to save
	renameOut = true;
	chain     = r => `dexvert[asFormat:poly/${r.flags.outType || _DEFAULT_INTERMEDIATE}]`;
}
