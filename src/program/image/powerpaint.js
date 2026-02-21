import {Program} from "../../Program.js";

export class powerpaint extends Program
{
	website   = "https://github.com/Sembiance/powerpaint";
	flags   = {
		format : "Which type to convert as, required."
	};
	bin       = "java";
	args      = async r => ["-jar", Program.binPath("powerpaint.jar"), "--convert", r.flags.format, r.inFile(), await r.outFile("out.png")];
	renameOut = true;
}
