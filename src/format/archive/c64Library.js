import {Format} from "../../Format.js";

export class c64Library extends Format
{
	name           = "C64 LiBRary";
	ext            = [".lbr"];
	forbidExtMatch = true;
	website        = "http://fileformats.archiveteam.org/wiki/LBR_(Commodore)";
	magic          = ["C64 LiBRary container"];
	converters     = ["DirMaster"];
}
