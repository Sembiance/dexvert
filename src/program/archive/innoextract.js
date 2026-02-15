import {xu} from "xu";
import {Program} from "../../Program.js";

export class innoextract extends Program
{
	website   = "https://github.com/dscharrer/innoextract";
	package   = "app-arch/innoextract";
	bin       = "innoextract";
	args      = r => ["--extract", "--output-dir", r.outDir({absolute : true}), r.inFile({absolute : true})];
	renameOut = false;
	notes     = "Additional inno format support vibe coded with claude code";
}
