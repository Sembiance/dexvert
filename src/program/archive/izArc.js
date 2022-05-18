import {xu} from "xu";
import {Program} from "../../Program.js";

export class izArc extends Program
{
	website   = "https://www.izarc.org/";
	loc       = "win2k";
	bin       = "c:\\Program Files\\IZArc\\IZARCE.exe";
	args      = r => ["-e", "-d", "-pc:\\out", r.inFile()];
	qemuData  = ({timeout : xu.MINUTE*2});
	renameOut = false;
}
