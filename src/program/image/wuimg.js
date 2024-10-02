import {Program} from "../../Program.js";

export class wuimg extends Program
{
	website    = "https://codeberg.org/kaleido/wuimg";
	package    = "media-gfx/wuimg";
	bin        = "wu";
	runOptions = ({virtualX : true, virtualXGLX : true});
	args       = r => ["write", "-d", r.outDir(), r.inFile()];
	renameOut  = true;
	chain      = "convert";
}
