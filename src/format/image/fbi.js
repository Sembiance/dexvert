import {Format} from "../../Format.js";

export class fbi extends Format
{
	name           = "FLIP Image";
	website        = "http://fileformats.archiveteam.org/wiki/FLIP";
	ext            = [".fbi"];
	forbidExtMatch = true;
	magic          = ["SysEx File", "FLIP Bitmap"];
	weakMagic      = true;
	converters     = ["recoil2png"];
}
