import {xu} from "xu";
import {Program} from "../../Program.js";

export class shockwave3DWorldConverter extends Program
{
	website = "https://github.com/tomysshadow/Shockwave-3D-World-Converter";
	loc     = "win7";
	bin     = "c:\\dexvert\\Shockwave3DWorldConverter\\Shockwave3DWorldConverter.exe";
	args    = r => [r.inFile()];
	osData  = {
		script : `
		$mainWindow = WindowRequire("Shockwave 3D World Converter 1.3.9", "", 10)
		MouseClick("left", 302, 302, 1, 0)

		Func SaveDialogOrErrors()
			WindowDismiss("Director Player Error", "", "{ESCAPE}")
			WindowFailure("", "Failed to Open File", -1, "{ESCAPE}")
			return WinActive("Export Wavefront OBJ File", "")
		EndFunc
		$saveWindow = CallUntil("SaveDialogOrErrors", ${xu.SECOND*20})
		If Not $saveWindow Then
			Exit 0
		EndIf

		Send("c:\\out\\out.obj{ENTER}")
		Func DismissWarnings()
			WindowDismiss("Locate replacement", "", "{ESCAPE}")
			WindowDismiss("Where is", "", "{ESCAPE}")
			WindowDismiss("Director Player Error", "", "y")
			return WinActive("", "Shockwave 3D World Converted Successfully!")
		EndFunc
		CallUntil("DismissWarnings", ${xu.MINUTE})`,
		timeout : xu.MINUTE*2
	};
	renameOut = {
		alwaysRename : true,
		renamer      : [({fn, originalInput}) => (originalInput && fn==="out.obj" ? [originalInput.name, ".obj"] : [fn])]
	};
	chain      = "?dexvert[asFormat:poly/wavefrontOBJ]";
	chainCheck = (r, chainFile) => chainFile.ext.toLowerCase()===".obj";
}
