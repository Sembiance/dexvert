import {Program} from "../../Program.js";

export class jar32 extends Program
{
	website   = "http://www.arjsoftware.com/jar.htm";
	loc       = "win7";
	bin       = "c:\\dexvert\\jar102\\jar32.exe";
	args      = r => ["x", r.inFile()];
	osData    = ({cwd : "c:\\out"});
	renameOut = false;
}
