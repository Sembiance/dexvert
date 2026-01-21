import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class accessSoftwareAP extends Format
{
	name    = "Access Software AP Archive";
	ext     = [".ap"];
	idCheck = async inputFile =>
	{
		if(inputFile.size<2)
			return false;
		
		const header = await fileUtil.readFileBytes(inputFile.absolute, 2);
		const numFiles = header.getUInt16LE();
		if(numFiles<2)
			return false;

		const minFileSize = (numFiles*4)+2;
		if(minFileSize>inputFile.size)
			return false;

		const fileTable = await fileUtil.readFileBytes(inputFile.absolute, minFileSize);
		for(let i=0;i<numFiles;i++)
		{
			if(fileTable.getUInt32LE(2+(i*4))>inputFile.size)
				return false;
		}

		return true;
	};
	converters = ["na_game_tool_extract[format:access_ap]"];
}
