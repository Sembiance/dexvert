import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class hellLib extends Format
{
	name    = "Hell: A Cayberpunk Thriller Library";
	ext     = [".pl"];
	idCheck = async inputFile =>
	{
		if(inputFile.size<6)
			return false;
		
		const header = await fileUtil.readFileBytes(inputFile.absolute, 6);
		const numFiles = header.getUInt16LE();
		if(numFiles===0)
			return false;

		const tocSize = numFiles*12;
		if((tocSize+4)>inputFile.size)
			return false;

		const tocOffset = header.getUInt32LE(2);
		if(tocOffset+tocSize>inputFile.size)
			return false;

		const fileTable = await fileUtil.readFileBytes(inputFile.absolute, tocSize, tocOffset);
		for(let i=0;i<numFiles;i++)
		{
			const fileOffset = fileTable.getUInt32LE(i*12);
			if(fileOffset<6 || fileOffset>tocOffset)
				return false;
		}

		return true;
	};
	converters = ["na_game_tool_extract[format:hell-lib]"];
}
