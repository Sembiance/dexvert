import {Program} from "../../Program.js";

export class mmex extends Program
{
	website   = "https://github.com/david47k/mmex";
	package   = "app-arch/cabextract";
	bin       = "mmex";
	args      = r => [r.inFile(), "-dump", "out"];
	cwd       = r => r.outDir();
	renameOut = false;
}
