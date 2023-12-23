import {xu} from "xu";
import {Program} from "../../Program.js";

export class izArc extends Program
{
	website   = "https://www.izarc.org/";
	loc       = "win2k";
	bin       = "c:\\Program Files\\IZArc\\IZARCE.exe";
	args      = r => ["-e", "-d", "-pc:\\out", r.inFile()];	// you can pass -snopasswd to use a password, but it doesn't make izarc not prompt for a password when that fails, so don't bother
	osData    = ({timeout : xu.MINUTE*2});
	renameOut = false;
}
