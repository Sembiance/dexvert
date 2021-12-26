import {Program} from "../../Program.js";

export class ancient extends Program
{
	website   = "https://github.com/temisu/ancient_format_decompressor";
	package   = "app-arch/ancient";
	bin       = "ancient";
	args      = async r => ["decompress", r.inFile(), await r.outFile("out")];
	renameOut = {preSensitive : true};
}
