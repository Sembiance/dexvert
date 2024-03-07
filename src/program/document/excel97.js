import {xu} from "xu";
import {Program} from "../../Program.js";

export class excel97 extends Program
{
	website  = "https://archive.org/details/office97standard_201912/";
	flags   = {
		outMethod : `How to output. Can specify 'print' to print to pdf, otherwise an .xls file is saved and chained to soffice.`
	};
	loc      = "win2k";
	bin      = "c:\\Program Files\\Microsoft Office\\Office\\EXCEL.EXE";
	args     = r => [r.inFile()];
	osData   = r => ({
		script : `
			Func MainWindowOrFailure()
				WindowFailure("Microsoft Excel", "Cannot open", -1, "{ENTER}")
				WindowFailure("Microsoft Excel", "This file is not in a recognizable format", -1, "{ESCAPE}")
				WindowDismiss("Microsoft Excel", "The workbook you opened contains automatic", "{ENTER}")
				WindowDismiss("File Not Found", "", "{ESCAPE}")
				return WinActive("[TITLE:Microsoft Excel - ]", "Save as")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*10})
			
			${r.flags.outMethod==="print" ? `
				Send("^p")
				$printWindow = WindowRequire("Print", "", 10)
				Send("{ENTER}")
			
				$savePDFWindow = WindowRequire("Save PDF File As", "", 5)
				Send("c:\\out\\out.pdf{ENTER}")
				WinWaitClose($savePDFWindow)
			` : `
				SendSlow("!fa")

				$saveAsWindow = WindowRequire("[TITLE:Save As]", "", 10)

				Sleep(200)
				Send("{TAB}{DOWN}{HOME}{ENTER}")
				Send("+{TAB}c:\\out\\outfile.xls{ENTER}")
				
				WinWaitClose($saveAsWindow, "", 5)`}

			Sleep(200)
			SendSlow("!fx")`
	});
	renameOut  = true;
	chain      = "?soffice[format:MS Excel 97][outType:pdf]";
	chainCheck = r =>
	{
		r.xlog.info`in chainCheck excel97 ${r.flags.outMethod}`;
		return r.flags.outMethod!=="print";
	};
}
