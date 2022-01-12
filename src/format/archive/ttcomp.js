import {Format} from "../../Format.js";

export class ttcomp extends Format
{
	name       = "TTComp Archive";
	website    = "http://fileformats.archiveteam.org/wiki/TTComp_archive";
	magic      = ["TTComp archive"];	// VERY weak, but alas.
	trustMagic = true;
	
	// music/thomasHermann is mis-identified as ttcomp
	forbiddenExt = [".thm"];
	idCheck      = inputFile => inputFile.preExt!==".thm";

	// mac binary files are also sometimes identified as this
	forbiddenMagic = ["MacBinary 2", "MacBinary II"];

	// NOTE: Deark also supports extraction of these, but because deark will also convert so many other formats and TTComp is a VERY weak magic identification, we don't include it here
	converters = ["ttdecomp"];
}
