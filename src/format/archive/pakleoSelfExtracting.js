import {Format} from "../../Format.js";

export class pakleoSelfExtracting extends Format
{
	name           = "PAKLEO Self-Extracting Archive";
	website        = "http://fileformats.archiveteam.org/wiki/PAKLEO";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["16bit DOS EXE PAKLEO SFX archive"];
	converters     = ["dosEXEExtract[exeArgs:-X +Y]"];
}
