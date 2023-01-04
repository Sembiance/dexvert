import {Program} from "../../Program.js";

export class dcopy extends Program
{
	website   = "https://github.com/pulkomandy/ddosutils";
	package   = "app-arch/ddosutils";
	bin       = "dcopy.exe";
	unsafe    = true;
	args      = r => [r.inFile(), "*.*", r.outDir({trailingSlash : true})];
	renameOut = false;
}
