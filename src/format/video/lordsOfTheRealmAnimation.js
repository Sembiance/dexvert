import {fileUtil} from "xutil";
import {Format} from "../../Format.js";

export class lordsOfTheRealmAnimation extends Format
{
	name       = "Lords of the Realm Animation";
	ext        = [".vas"];
	idCheck    = async inputFile =>
	{
		if(inputFile.size<16)
			return false;
	
		const bytes = await fileUtil.readFileBytes(inputFile.absolute, 2);
		return [0x00, 0x01].includes(bytes[0]) && bytes[1]===0x00;
	};
	converters = ["na_game_tool[format:vas]"];
}

