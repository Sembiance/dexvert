import {Program} from "../../Program.js";

export class projectorRays extends Program
{
	website   = "https://github.com/ProjectorRays/ProjectorRays";
	package   = "app-arch/ProjectorRays";
	bin       = "projectorrays";
	args      = async r => ["decompile", "-o", await r.outFile("out.dir"), r.inFile()];
	renameOut = true;
}
