import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class celestialImpactDXV extends Format
{
	name    = "Celestial Impact DXV Video";
	ext     = [".dxv"];
	idCheck = async inputFile =>
	{
		if(inputFile.size<1912)
			return false;
		
		const header = await fileUtil.readFileBytes(inputFile.absolute, 8);
		if(header.getUInt32LE()===0 || header.getUInt32LE()>10000)
			return false;

		if(header.getUInt32LE(4)===0 || header.getUInt32LE(4)>282_344)
			return false;

		return true;
	};
	converters = ["na_game_tool[format:dxv]"];
}
