import {Program} from "../../Program.js";

export class vort2ppm extends Program
{
	website    = "https://ftp.gwdg.de/pub/misc/grafik/vogl/vort.tar.gz";
	package    = "media-gfx/vort";
	bin        = "vort2ppm";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.ppm")});
	renameOut  = true;
	chain      = "convert";
}
