import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";

export class doomMUS2mp3 extends Program
{
	website = "http://slade.mancubus.net/";
	unsafe  = true;
	loc     = "winxp";
	bin     = "c:\\dexvert\\slade\\SLADE.exe";
	args    = async r =>
	{
		// SLADE needs the file in a ZIP file
		r.zipFilePath = await fileUtil.genTempPath(r.f.root, ".zip");
		await runUtil.run("zip", ["-r", r.zipFilePath, r.inFile()], {cwd : r.f.root});
		await r.f.add("aux", r.zipFilePath);
		return [path.basename(r.zipFilePath)];
	};
	qemuData = ({
		script : `
			WinWaitActive("[TITLE:SLADE; CLASS:wxWindowNR]", "", 10)
			Sleep(4000)
			WaitForControl("[TITLE:SLADE; CLASS:wxWindowNR]", "", "[CLASS:Button; TEXT:Entries]", ${xu.SECOND*10})
			Sleep(4000)
			Local $entriesPOS = ControlGetPos("[TITLE:SLADE; CLASS:wxWindowNR]", "", "[CLASS:Button; TEXT:Entries]")
			MouseClick("right", $entriesPOS[0]+26, $entriesPOS[1]+104, 1)
			Sleep(750)
			Send("{UP}")
			Sleep(500)
			Send("{RIGHT}")
			Sleep(500)
			Send("{ENTER}")
			Sleep(1000)
			Send("^e")

			WinWaitActive("Export Entry", "", 10)
			WaitForControl("Export Entry", "", "[CLASS:Edit; INSTANCE:1]", ${xu.SECOND*10})
			ControlSetText("Export Entry", "", "[CLASS:Edit; INSTANCE:1]", "c:\\out\\out.mid")

			Sleep(200)
			ControlClick("Export Entry", "", "[CLASS:Button; TEXT:&Save]")

			WinWaitClose("Export Entry", "", 10)

			Send("!f")
			Sleep(200)
			Send("x")

			WinWaitActive("Unsaved Changes", "", 10)
			WaitForControl("Unsaved Changes", "", "[CLASS:Button; TEXT:&No]", ${xu.SECOND*10})
			ControlClick("Unsaved Changes", "", "[CLASS:Button; TEXT:&No]")

			WinWaitClose("[TITLE:SLADE; CLASS:wxWindowNR]", "", 100)
			
			WaitForPID(ProcessExists("SLADE.exe"), ${xu.MINUTE})`
	});
	chain = "timidity";
}
