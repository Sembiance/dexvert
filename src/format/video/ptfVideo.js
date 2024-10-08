import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class ptfVideo extends Format
{
	name           = "PTF Video";
	website        = "https://wiki.multimedia.cx/index.php/Flic_Video#Under_a_Killing_Moon_PTF";
	ext            = [".ptf"];
	forbidExtMatch = true;
	magic          = ["PTF Video"];
	idCheck        = async inputFile => inputFile.size>=4 && (await fileUtil.readFileBytes(inputFile.absolute, 4)).getUInt32LE()===inputFile.size;
	converters     = ["na_game_tool[format:ptf]"];
}
