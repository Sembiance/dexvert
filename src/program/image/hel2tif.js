import {Program} from "../../Program.js";
import {path} from "std";

export class hel2tif extends Program
{
	website   = "https://discmaster.textfiles.com/browse/657/FM%20Towns%20Free%20Software%20Collection%2010.iso/t_os/tool/hel2tif";
	package   = "media-gfx/hel2tif";
	bin       = "hel2tif";
	args      = r => ["-o", path.join(r.outDir(), "out"), "-32768", r.inFile()];
	chain     = "convert[format:tiff]";
	renameOut = false;
}
