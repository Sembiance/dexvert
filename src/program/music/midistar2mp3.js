import {Program} from "../../Program.js";

export class midistar2mp3 extends Program
{
	website = "https://github.com/Sembiance/midistar2mid";
	package = "media-sound/midistar2mid";
	bin     = "midistar2mid";
	args    = async r => [r.inFile(), await r.outFile("out.mid")];
	chain   = "timidity";
}
