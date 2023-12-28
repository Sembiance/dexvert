import {Format} from "../../Format.js";

export class ttcomp extends Format
{
	name       = "TTComp Archive";
	website    = "http://fileformats.archiveteam.org/wiki/TTCOMP";
	magic      = ["TTComp archive"];	// VERY weak, but alas.
	trustMagic = true;
	packed     = true;
	
	// music/thomasHermann is mis-identified as ttcomp
	forbiddenExt = [".thm"];
	idCheck      = inputFile => inputFile.preExt!==".thm";

	// mac binary files are also sometimes identified as this
	forbiddenMagic = [/MacBinary/];

	converters = ["ttdecomp"];	// "deark[module:dclimplode]" also works, but it will take almost any file as input
}
