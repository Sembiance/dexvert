import {Format} from "../../Format.js";

export class kofaxGroup4 extends Format
{
	name       = "Kofax Group 4";
	website    = "http://fileformats.archiveteam.org/wiki/Kofax_Group_4";
	ext        = [".kfx"];
	magic      = ["Kofax Group 4 bitmap", "Kofax Group 4 :kfx:"];
	converters = ["nconvert[format:kfx]", "hiJaakExpress[matchType:magic]"];
}
