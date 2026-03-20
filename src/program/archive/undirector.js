import {Program} from "../../Program.js";

export class undirector extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	package   = "app-arch/undirector";
	bin       = "undirector";
	args      = r => [r.inFile(), r.outDir()];
	renameOut = false;
}
