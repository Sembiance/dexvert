import {Format} from "../../Format.js";

export class ttcomp extends Format
{
	name       = "TTComp Archive";
	website    = "http://fileformats.archiveteam.org/wiki/TTCOMP";
	magic      = ["TTComp archive"];	// VERY weak, but alas.
	priority   = this.PRIORITY.LOW;
	trustMagic = true;
	packed     = true;
	fallback   = true;	// lots of things match to TTComp that shouldn't, so we mark it as a fallback format

	// music/thomasHermann is mis-identified as ttcomp
	forbiddenExt = [".thm"];
	idCheck      = inputFile => inputFile.preExt!==".thm";

	// mac binary files are also sometimes identified as this
	forbiddenMagic = [/MacBinary/];

	converters = ["ttdecomp"];	// "deark[module:dclimplode]" also works, but it will take almost any file as input
}
