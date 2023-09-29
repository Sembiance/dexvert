import {Program} from "../../Program.js";

export class word97 extends Program
{
	website  = "https://archive.org/details/office97standard_201912/";
	notes    = "revisableFormText converter from: http://www.gmayor.com/downloads.htm";
	loc      = "win2k";
	bin      = "c:\\Program Files\\Microsoft Office\\Office\\WINWORD.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("[TITLE:Microsoft Word - ]", "", 10)
			
			SendSlow("!fa")

			$saveAsWindow = WindowRequire("[TITLE:Save As]", "", 10)

			Sleep(200)
			Send("c:\\out\\outfile.doc{ENTER}")
			
			WinWaitClose($saveAsWindow, "", 5)
			Sleep(200)

			SendSlow("!fx")`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:document/wordDoc]";
}
