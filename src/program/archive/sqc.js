import {xu} from "xu";
import {Program} from "../../Program.js";

export class sqc extends Program
{
	website   = "https://www.speedproject.com/download/old/";
	loc       = "win2k";
	bin       = "c:\\Program Files\\SpeedProject\\Squeez 5\\sqc.exe";
	args      = r => ["x", r.inFile()];
	qemuData  = ({cwd : "c:\\out", timeout : xu.MINUTE*2});
	renameOut = false;
}
