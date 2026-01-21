import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class flkAnimation extends Format
{
	name    = "FLK Animation";
	ext     = [".flk"];
	idCheck = async inputFile =>
	{
		if(inputFile.size<20)
			return false;
		
		const header = await fileUtil.readFileBytes(inputFile.absolute, 20);
		const numFrames = header.getUInt32LE();
		if(numFrames===0 || numFrames>2000)
			return false;

		if([header.getUInt32LE(8), header.getUInt32LE(12)].some(v => v===0 || v>1024))
			return false;

		if(header.getUInt32LE(16)!==(numFrames*64))
			return false;

		return true;
	};
	converters = ["na_game_tool[format:flk]"];
}
