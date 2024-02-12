import {Program} from "../../Program.js";

export class sixel2png extends Program
{
	website    = "https://github.com/saitoha/libsixel";
	package    = "media-libs/libsixel";
	bin        = "sixel2png";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.png")});
	renameOut  = true;
}
