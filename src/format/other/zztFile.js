import {Format} from "../../Format.js";

export class zztFile extends Format
{
	name           = "ZZT File";
	website        = "http://fileformats.archiveteam.org/wiki/ZZT";
	ext            = [".zzt"];
	forbidExtMatch = true;
	magic          = ["ZZT Game Creation System", "ZZT World"];
	weakMagic      = true;
	converters     = ["zztScreenshotter"];
}
