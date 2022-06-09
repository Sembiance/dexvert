import {xu} from "xu";
import {Program} from "../../Program.js";

export class luraWave extends Program
{
	website  = "https://archive.org/download/plug-in-power-pack-for-netscape-communicator/Plug-In%20Power%20Pack%20for%20Netscape%20Communicator.iso/plugins%2Flw20free.exe";
	loc      = "win2k";
	bin      = "c:\\Program Files\\LuraWave20\\LuRaWave.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
		$mainWindow = WindowRequire("LURAWAVE for Windows", "", 5)
		Send("^s")

		$saveAsWindow = WindowRequire("File Save", "", 5)
		Send("c:\\out\\out.tif{TAB}{TAB}{TAB}{END}{ENTER}")

		WinWaitClose($saveAsWindow, "", 10)
		WinWaitActive($mainWindow, "", 3)

		WinClose($mainWindow, "")`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:image/tiff]";
}
