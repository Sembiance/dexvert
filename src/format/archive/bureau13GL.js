import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class bureau13GL extends Format
{
	name    = "Bureau 13 GL Archive";
	ext     = [".gl"];
	idCheck = async inputFile =>
	{
		if(inputFile.size<4)
			return false;
		
		const header = await fileUtil.readFileBytes(inputFile.absolute, 4);
		return header.getUInt16LE()>0 && header.getUInt16LE()<10000 && header.getUInt16LE(2)>6;
	};
	converters = ["na_game_tool_extract[format:b13_gl]"];
}
