import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class arkOfTimeAN extends Format
{
	name       = "Ark of Time AN Video";
	website    = "https://wiki.multimedia.cx/index.php/Ark_of_Time_AN";
	ext        = [".an"];
	idCheck    = async inputFile => inputFile.size>5 && (await fileUtil.readFileBytes(inputFile.absolute, 3, 2)).indexOfX([0x00, 0x00, 0x12])===0;
	converters = ["na_game_tool[format:ark-an]"];
}
