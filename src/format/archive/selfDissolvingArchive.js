import {Format} from "../../Format.js";

export class selfDissolvingArchive extends Format
{
	name       = "Self-Dissolving Archive";
	website    = "http://fileformats.archiveteam.org/wiki/SDA";
	ext        = [".sda"];
	magic      = ["Self-Dissolving compressed Archive", /^Arc CBM SFX$/];
	converters = ["unar[type:Arc CBM SFX]", "DirMaster[matchType:magic]"];
}
