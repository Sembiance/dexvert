import {Format} from "../../Format.js";

export class selfExtractingLHA extends Format
{
	name       = "Self-Extracting LHA";
	website    = "http://fileformats.archiveteam.org/wiki/SFX";
	ext        = [".sfx"];
	magic      = ["Self-Extracting LHA Archive", /^fmt\/1558( |$)/];
	converters = ["unar", "DirMaster[matchType:magic]"];
}
