import {Format} from "../../Format.js";

export class c64Library extends Format
{
	name           = "C64 LiBRary";
	website        = "http://fileformats.archiveteam.org/wiki/LBR_(Commodore)";
	ext            = [".lbr"];
	forbidExtMatch = true;
	magic          = ["C64 LiBRary container"];
	converters     = ["DirMaster"];
}
