import {Program} from "../../Program.js";

export class extractCompressedFS extends Program
{
	website   = "https://launchpad.net/ubuntu/+source/cloop/";
	package   = "app-arch/cloop-utils";
	bin       = "extract_compressed_fs";
	args      = async r => [r.inFile(), await r.outFile("out")];
	renameOut = true;
}
