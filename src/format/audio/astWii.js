import {xu} from "xu";
import {Format} from "../../Format.js";

export class astWii extends Format
{
	name       = "AST Wii Audio";
	website    = "http://fileformats.archiveteam.org/wiki/Nintendo_GameCube_/_Wii_AST";
	ext        = [".ast", ".asf"];
	magic      = ["Wii sound data", "FIFA 2004 audio file", "AST (Audio Stream) (ast)"];
	converters = ["zxtune123[matchType:magic]", "vgmstream"];
}
