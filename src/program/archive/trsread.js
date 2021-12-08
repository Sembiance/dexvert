import {Program} from "../../Program.js";

export class trsread extends Program
{
	website   = "http://www.trs-80emulators.com/trsread-trswrite.html";
	loc       = "winxp";
	bin       = "trsread.exe";
	args      = r => ["-e", "-s", "-i", r.inFile()];
	qemuData  = ({cwd : "c:\\out"});
	renameOut = false;
}
