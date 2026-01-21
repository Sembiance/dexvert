import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class alienVirusAnimation extends Format
{
	name    = "Alien Virus Animation";
	ext     = [".ani"];
	idCheck = async inputFile =>
	{
		if(inputFile.size<14)
			return false;
		
		const header = await fileUtil.readFileBytes(inputFile.absolute, 14);
		return header.getUInt32LE()===inputFile.size && header.getUInt16LE(4)===0x3333 && header.getUInt16LE(12)===8;
	};
	converters = ["na_game_tool[format:av_ani]"];
}
