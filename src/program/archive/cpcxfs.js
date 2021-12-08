import {Program} from "../../Program.js";

export class cpcxfs extends Program
{
	website    = "http://www.cpcwiki.eu/forum/applications/cpcxfs/";
	package    = "app-arch/cpcxfs";
	bin        = "cpcxfs";
	args       = r => [r.inFile(), "-mg", "*.*"];
	cwd        = r => r.outDir();
	runOptions = ({env : {TERM : "xterm"}});
	renameOut  = false;
}
