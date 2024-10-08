import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class ca2Video extends Format
{
	name       = "CA2 Video";
	website    = "https://wiki.multimedia.cx/index.php/CA2";
	ext        = [".ca2"];
	idCheck    = async inputFile => inputFile.size>4 && (await fileUtil.readFileBytes(inputFile.absolute, 4)).indexOfX([0x80, 0x00, 0x00, 0x00])===0;
	converters = ["na_game_tool[format:ca2]"];
}
