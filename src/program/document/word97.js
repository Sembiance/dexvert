import {Program} from "../../Program.js";

export class word97 extends Program
{
	website  = "https://archive.org/details/office97standard_201912/";
	notes    = "revisableFormText converter from: http://www.gmayor.com/downloads.htm";
	loc      = "win2k";
	bin      = "c:\\Program Files\\Microsoft Office\\Office\\WINWORD.EXE";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			WinWaitActive("[TITLE:Microsoft Word - ]", "", 10)

			Send("!f")
			Sleep(200)
			Send("a")

			WinWaitActive("[TITLE:Save As]", "", 10)

			Sleep(200)
			Send("c:\\out\\outfile.doc{ENTER}")
			
			WinWaitClose("[TITLE:Save As]", "", 10)
			Sleep(200)

			Send("!f")
			Sleep(200)
			Send("x")
			
			WinWaitClose("[TITLE:Microsoft Word - ]", "", 10)`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:document/wordDoc]";
}
