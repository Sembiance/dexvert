import {Program} from "../../Program.js";

export class mmvid_extractor extends Program
{
	website        = "https://github.com/einstein95/mmvid_extractor";
	package        = "app-arch/mmvid_extractor";
	bin            = "mmvid_extractor";
	args           = r => [r.inFile()];
	cwd            = r => r.outDir();
	mirrorInToCWD  = "copy";
	forbidChildRun = true;
	renameOut      = false;
}
