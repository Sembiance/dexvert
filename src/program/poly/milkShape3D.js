import {xu} from "xu";
import {Program} from "../../Program.js";

// Get new coordinates for new menu items by looking at sandbox/app/milkShape3D_MenuCoords.png in gimp
const _FORMATS =
{
	doom3Mesh    : {menuY : 520},
	dxf          : {menuY : 324, window : {name : "MilkShape 3D 1.8.4", text : "Do you want to delete", dismiss : "Y"}},
	fbx          : {menuY : 342, window : {name : "FBX Import", dismiss : "{ENTER}"}},
	ghoul2       : {menuY : 451, window : {name : "Ghoul2 Model Import Options", dismiss : "{ENTER}"}},
	lightWave    : {menuY : 307, window : {name : "LightWave LWO Import", dismiss : `${"{TAB}".repeat(9)}{SPACE}{TAB}{SPACE}{TAB}{SPACE}{ENTER}`}},
	mayaASCII    : {menuY : 504},
	quake2Model  : {menuY : 44},
	quake3Model  : {menuY : 59},
	rtcwMDC      : {menuY : 538},
	softimageXSI : {menuY : 757, window : {name : "SOFTIMAGE", dismiss : "{TAB}{ENTER}", preOpenDismiss : "{TAB}{SPACE}"}},	// WARNING: Have no sample files yet that this works with
	wavefront    : {menuY : 257}
};

export class milkShape3D extends Program
{
	website   = "http://www.milkshape3d.com/";
	loc       = "winxp";
	bin       = "c:\\Program Files\\MilkShape 3D 1.8.4\\ms3d.exe";
	flags   = {
		format : "Which format is the input model"
	};
	args      = r => [r.inFile()];
	osData    = r => ({
		script : `
			$mainWindow = WindowRequire("MilkShape 3D 1.8.4 - untitled", "", 15)

			MouseClick("left", 14, 29, 1, 0)
			MouseMove(40, 147, 0)
			MouseMove(214, 145, 5)
			MouseClick("left", 206, ${_FORMATS[r.flags.format].menuY}, 1, 5)

			${_FORMATS[r.flags.format].window?.preOpenDismiss ? `WindowDismissWait("${_FORMATS[r.flags.format].window.name}", "${_FORMATS[r.flags.format].window.text || ""}", 5, "${_FORMATS[r.flags.format].window.preOpenDismiss}")` : ""}

			$openWindow = WindowRequire("Open", "", 10)
			Send("c:\\in\\${r.inFile()}{ENTER}")
			WinWaitClose($openWindow, "", 15)
			Sleep(1000)

			Func MainWindowOrFailure()
				WindowFailure("Error", "", -1, "{ENTER}")
				${_FORMATS[r.flags.format].window ? `WindowDismiss("${_FORMATS[r.flags.format].window.name}", "${_FORMATS[r.flags.format].window.text || ""}", "${_FORMATS[r.flags.format].window.dismiss}")` : ""}
				return WinActive($mainWindow, "")
			EndFunc
			CallUntil("MainWindowOrFailure", ${xu.SECOND*10})
			
			Send("^+s")
			$saveWindow = WindowRequire("Save As", "", 10)
			Send("c:\\out\\out.ms3d{ENTER}")
			WinWaitClose($saveWindow, "", 10)

			WaitForStableFileSize("c:\\out\\out.ms3d", ${xu.SECOND*3}, ${xu.SECOND*30})
			Send("!f")
			Sleep(250)
			Send("x")`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:poly/milkShape3DModel]";
}
