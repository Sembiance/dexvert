import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class coktelVisionSTK extends Format
{
	name    = "Coktel Vision STK Archive";
	ext     = [".stk"];
	idCheck = async inputFile =>
	{
		if(inputFile.size<6)
			return false;
		
		const header = await fileUtil.readFileBytes(inputFile.absolute, 6);
		const numFiles = header.getUInt16LE();
		if(numFiles===0 || numFiles>10000)
			return false;

		const tocSize = numFiles*22;
		if((tocSize+2)>inputFile.size)
			return false;

		let totalSize = 0;
		const fileTable = await fileUtil.readFileBytes(inputFile.absolute, tocSize, 2);
		for(let i=0;i<numFiles;i++)
		{
			totalSize += fileTable.getUInt32LE((i*22)+13);
			const fileOffset = fileTable.getUInt32LE((i*22)+17);
			if(fileOffset<(tocSize+2) || fileOffset>inputFile.size)
				return false;
		}

		if((totalSize+tocSize+2)>inputFile.size)
			return false;

		return true;
	};
	converters = ["na_game_tool_extract[format:stk]"];
}
