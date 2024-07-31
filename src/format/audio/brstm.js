import {xu} from "xu";
import {Format} from "../../Format.js";

export class brstm extends Format
{
	name       = "BRSTM Wii Audio";
	website    = "http://fileformats.archiveteam.org/wiki/Nintendo_GameCube_/_Wii_BRSTM";
	ext        = [".brstm"];
	magic      = ["Nintendo Wii BRSTM audio file", "BRSTM audio"];
	converters = ["zxtune123", "vgmstream"];
}
