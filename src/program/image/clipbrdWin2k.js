import {Program} from "../../Program.js";

export class clipbrdWin2k extends Program
{
	website  = "https://microsoft.com";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\WINNT\\system32\\clipbrd.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("ClipBook Viewer", "", 10)

			WindowDismissWait("Clear Clipboard", "", 20, "N")

			; switch to the actual clip we opened
			WinWaitActive($mainWindow, "", 10)
			SendSlow("!w1")
			Sleep(2000)

			; open mspaint, paste it and save it as a png
			SaveClipboardWithMSPaint("WINNT", "c:\\out\\out.png")

			WinWaitActive($mainWindow, "", 10)
			SendSlow("!fx")`});
	renameOut = true;
	chain     = "dexvert[asFormat:image/bmp] -> autoCropImage";
}
