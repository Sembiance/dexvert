import {xu} from "xu";
import {Program} from "../../Program.js";
import {serialUtil} from "/mnt/compendium/DevLab/xpriv/xpriv.js";
import {fileUtil} from "xutil";

export class IsoBuster extends Program
{
	website   = "https://www.isobuster.com/isobuster.php";
	loc       = "wine";
	bin       = "c:\\Program Files\\Smart Projects\\IsoBuster\\IsoBuster.exe";
	exclusive = "wine";
	
	// IsoBuster command line options: https://www.isobuster.com/help/use_of_command_line_parameters
	args = r => [`/ef:all:C:\\out${r.wineCounter}`, r.inFile(), "/c", "/ep:ren", "/ep:rei", "/ep:oeo", "/nosplash", "/nodrives"];
	
	wineData = {
		timeout : xu.MINUTE*10,	// IsoBuster can take a LONG time to run, but 10 minutes should be plenty for any file
		
		// normally, if the command works, we don't need to do anything at all with the script, but if a bad file is sent it might show an error we need to cancel
		script : `
			Func PreOpenWindows()
				$registerWindow = WinGetHandle("Registration will enable IsoBuster PRO functionality", "")
				If $registerWindow Not = 0 Then
					WinMove($registerWindow, "", 0, 0)
					ControlSetText($registerWindow, "", "[CLASS:TEdit; INSTANCE:1]", "${serialUtil.getSerial("isoBuster")["5.2"].email}")
					ControlSetText($registerWindow, "", "[CLASS:TEdit; INSTANCE:3]", "${serialUtil.getSerial("isoBuster")["5.2"].registrationid}")
					ControlSetText($registerWindow, "", "[CLASS:TEdit; INSTANCE:2]", "${serialUtil.getSerial("isoBuster")["5.2"].key}")
					ControlClick($registerWindow, "", "[CLASS:TButton; INSTANCE:4]")
					WinWaitClose($registerWindow, "", 5)
				EndIf

				WindowDismiss("Friendly warning", "", "{ENTER}")

				$noFilesWindow = WinActive("No file systems and/or files found", "")
				If $noFilesWindow Not = 0 Then
					ControlClick($noFilesWindow, "", "[TEXT:&Cancel]")
					WinWaitClose($noFilesWindow, "", 3)
				EndIf
			EndFunc
			CallUntil("PreOpenWindows", ${xu.SECOND*4})
			
			WaitForPID("IsoBuster.exe", ${xu.MINUTE*3})`
	};

	// Some old apple disk copy images like archive/appleDiskCopy/Portal1.image produces these info files which we don't care about
	postExec = async r =>
	{
		const fileOutputPaths = await fileUtil.tree(r.outDir({absolute : true}), {nodir : true});
		for(const fileOutputPath of fileOutputPaths)
		{
			if(fileOutputPath.endsWith(":AFP_AfpInfo"))
				await fileUtil.unlink(fileOutputPath);
		}
	};

	renameOut = false;
}
