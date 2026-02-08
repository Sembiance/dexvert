import {xu} from "xu";
import {Program} from "../../Program.js";

export class innoextract extends Program
{
	website   = "https://github.com/dscharrer/innoextract";
	package   = "app-arch/innoextract";
	bin       = "innoextract";
	args      = r => ["--extract", "--output-dir", r.outDir(), r.inFile()];
	renameOut = false;
}
