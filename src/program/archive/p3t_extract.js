import {xu} from "xu";
import {Program} from "../../Program.js";

export class p3t_extract extends Program
{
	website   = "https://github.com/hoshsadiq/ps3theme-p3t-extract";
	package   = "dev-lang/php";
	bin       = "php";
	args      = r => ["-f", Program.binPath("p3t_extract/p3t_extract.php"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = true;
}
