import {Format} from "../../Format.js";

export class pcx2com extends Format
{
	name           = "PCX2COM Image";
	website        = "http://fileformats.archiveteam.org/wiki/PCX2COM";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["16bit COM executable PCX2COM", "deark: pcx2com"];
	converters     = ["deark[module:pcx2com][renameOut] -> dexvert[asFormat:image/pcx"];
}
