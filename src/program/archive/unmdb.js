import {xu} from "xu";
import {Program} from "../../Program.js";

export class unmdb extends Program
{
	website = "https://github.com/mdbtools/mdbtools";
	package = "app-office/mdbtools";
	bin     = Program.binPath("unmdb");
	args    = r => ["--", r.inFile(), r.outDir()];
}
