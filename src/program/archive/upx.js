import {xu} from "xu";
import {Program} from "../../Program.js";

export class upx extends Program
{
	website   = "https://upx.github.io/";
	package   = "app-arch/upx-bin";
	bin       = "upx";
	args      = async r => ["-d", r.inFile(), "-o", await r.outFile("outfile")];
	renameOut = false;
}
