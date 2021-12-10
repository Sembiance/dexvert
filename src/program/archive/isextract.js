import {xu} from "xu";
import {Program} from "../../Program.js";

export class isextract extends Program
{
	website    = "https://github.com/OmniBlade/isextract";
	package    = "app-arch/isextract";
	bin        = "isextract";
	args       = r => ["x", r.inFile(), r.outDir()];
	runOptions = ({timeout : xu.MINUTE*2});
	renameOut  = false;
}
