import {xu} from "xu";
import {Program} from "../../Program.js";

export class ilbm2frames extends Program
{
	website    = "https://github.com/Sembiance/ilbm2frames";
	package    = "media-gfx/ilbm2frames";
	unsafe     = true;
	//bin        = "/mnt/compendium/DevLab/apps/ilbm2frames/ilbm2frames";
	bin        = "ilbm2frames";
	runOptions = ({virtualX : true});
	args       = r => ["--fps", "20", "--limitSeconds", "5", r.inFile(), r.outDir()];
	renameOut  = false;
}
