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

	// IsoBuster can take a LONG time to run, but 20 minutes should be plenty for any file
	qemuData = () => ({timeout : xu.MINUTE*20});

	renameOut = false;
}
