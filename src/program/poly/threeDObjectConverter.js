import {xu} from "xu";
import {Program} from "../../Program.js";

const _OUT_TYPES = {
	threeDStudio   : {keys : `3${"{DOWN}".repeat(8)}`, ext : ".3ds"},		// worked good for most formats, didn't work for polygonFileFormat bunny
	direct3DObject : {keys : `d${"{DOWN}".repeat(7)}`, ext : ".x"},
	quickDraw3D    : {keys : `q${"{DOWN}".repeat(3)}`, ext : ".3dmf"},		// doesn't seem to support color/textures, but good compatibility for formats that don't need that
	wavefrontOBJ   : {keys : `w{DOWN}`, ext : ".obj"}
};

const _OUT_TYPE_DEFAULT = "threeDStudio";

export class threeDObjectConverter extends Program
{
	website = "http://3doc.i3dconverter.com/";
	loc     = "win7";
	bin     = "c:\\Program Files (x86)\\3D Object Converter 10.60\\3dconverter.exe";
	flags   = {
		outType : "Specify which format to output to"
	};
	args      = r => [r.inFile()];		// flags: http://3doc.i3dconverter.com/features.html
	osData  = r => ({
		script : `
			Func MainWindowOrFailure()
				; There isn't any way to determine if these are fatal or not because the 'text' isn't really there and can't be easily read, so just dismiss it and hope
				WindowDismiss("Information", "", "{ENTER}")
				WindowDismiss("Warning", "", "{ENTER}")
				return WinActive("3D Object Converter v10.60     [ ", "");
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*5})
			If Not $mainWindow Then
				Exit 0
			EndIf

			Send("!f")
			Send("s")

			$saveWindow = WindowRequire("Save As", "", 10)
			Send("{TAB}{DOWN}${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].keys}{ENTER}+{TAB}c:\\out\\out${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].ext}{ENTER}")
			WinWaitClose($saveWindow, "", 120)
			WaitForStableFileSize("c:\\out\\out${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].ext}", ${xu.SECOND*3}, ${xu.MINUTE*2})`
	});
	renameOut = true;
	chain     = r => `dexvert[asFormat:poly/${r.flags.outType || _OUT_TYPE_DEFAULT}]`;
}
