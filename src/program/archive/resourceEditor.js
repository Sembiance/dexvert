import {xu} from "xu";
import {Program} from "../../Program.js";

export class resourceEditor extends Program
{
	website  = "http://melander.dk/reseditor/";
	loc      = "wine";
	bin      = "c:\\dexvert\\ResourceEditor\\ResourceEditor.exe";
	args     = r => [r.inFile()];
	notes    = "This broke in 86Box. It's flaky in wine too, thanks to xdotool being total utter shit. So currently nothing is using this";
	wineData = {
		script :
		[
			{ op : "windowRequire", matcher : /^Resource Editor by Anders Melander/, windowid : "mainWindow"},
			{ op : "delay", duration : xu.SECOND*2},
			{ op : "type", windowid : "mainWindow", text : `{Alt_L}f` },
			{ op : "delay", duration : 250},
			{ op : "type", windowid : "mainWindow", interval : 100, text : `{Down}{Down}{Down}{Down}{Return}` },
			{ op : "windowRequire", matcher : /^Save resource file/, windowid : "saveWindow"},
			{ op : "delay", duration : xu.SECOND*2},
			{ op : "type", windowid : "saveWindow", text : `{Tab}{End}{Return}` },
			{ op : "delay", duration : xu.SECOND},
			{ op : "type", windowid : "saveWindow", text : `{Shift_L+Tab}c:\\out.rc{Return}` }
		]
	};
	osData   = ({
		script : `
			WinWaitActive("Resource Editor", "", 10)

			AutoItSetOption("SendKeyDelay", 20)

			SendSlow("!f")
			Sleep(250)
			Send("{DOWN}{DOWN}{DOWN}{DOWN}{ENTER}")

			WinWaitActive("Save resource file", "", 10)

			Sleep(250)

			Send("{TAB}{DOWN}{DOWN}{DOWN}{DOWN}{ENTER}")
			Sleep(100)
			Send("+{TAB}c:\\out\\out.rc{TAB}{TAB}{TAB}{TAB}{DOWN}{ENTER}")

			WinWaitClose("Save resource file", "", 10)

			Sleep(200)
			
			SendSlow("!fx", 250)`
	});
	renameOut = {
		alwaysRename : true,
		renamer      : [({fn, originalInput}) => (originalInput && fn==="out.rc" ? [originalInput.name, ".rc"] : [fn])]
	};
}
