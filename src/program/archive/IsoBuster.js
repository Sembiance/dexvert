import {xu} from "xu";
import {Program} from "../../Program.js";

export class IsoBuster extends Program
{
	website = "https://www.isobuster.com/isobuster.php";
	unsafe  = true;	// super slow
	loc     = "winxp";
	bin     = "c:\\Program Files\\Smart Projects\\IsoBuster\\IsoBuster.exe";

	// IsoBuster command line options: https://www.isobuster.com/help/use_of_command_line_parameters
	args = r => ["/ef:all:C:\\out", r.inFile(), "/c", "/ep:ren", "/ep:rei", "/ep:oeo"];
	
	qemuData = ({
		timeout : xu.MINUTE*10,	// IsoBuster can take a LONG time to run, but 10 minutes should be plenty for any file
		
		// normally, if the command works, we don't need to do anything at all with the script, but if a bad file is sent it might show an error we need to cancel (http://retromission.com/view/3/World's%20Best%20Butts%20(1995).iso/viewers/pep13.zip/SERIOUS1.BIN)
		script : `
			Local $errorVisible = WinWaitActive("No file systems and/or files found", "", 10)
			If $errorVisible Not = 0 Then
				ControlClick("No file systems and/or files found", "", "[TEXT:&Cancel]")
			EndIf
			
			WaitForPID(ProcessExists("IsoBuster.exe"), ${xu.MINUTE*10})`
	});

	renameOut = false;
}
