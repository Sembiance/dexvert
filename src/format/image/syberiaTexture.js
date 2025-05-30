import {Format} from "../../Format.js";

export class syberiaTexture extends Format
{
	name       = "Syberia Texture";
	website    = "http://fileformats.archiveteam.org/wiki/Syberia_Texture";
	ext        = [".syj"];
	magic      = ["deark: syberia_syj"];
	converters = ["deark[module:syberia_syj]"];
}
