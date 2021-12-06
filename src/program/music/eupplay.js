import {Program} from "../../Program.js";

export class eupplay extends Program
{
	website    = "https://github.com/gzaffin/eupmini";
	package    = "media-sound/eupmini";
	unsafe     = true;
	bin        = "eupplay";
	args       = async r => ["-o", await r.outFile("out.wav"), r.inFile()];
	runOptions = ({env : {SDL_AUDIODRIVER : "disk"}});
	chain      = "sox";
}
