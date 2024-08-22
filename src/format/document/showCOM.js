import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class showCOM extends Format
{
	name           = "SHOW (Gary M. Raymond)";
	website        = "http://fileformats.archiveteam.org/wiki/SHOW_(Gary_M._Raymond)";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["16bit COM executable SHOW"];
	idCheck        = async inputFile =>
	{
		if((await fileUtil.readFileBytes(inputFile.absolute, 1, -1))[0]!==0x1A)
			return false;

		if(inputFile.size<4)
			return false;
		
		const offset = (await fileUtil.readFileBytes(inputFile.absolute, 2, 1)).getUInt16LE(0);
		if(inputFile.size<(offset+4))
			return false;

		if((await fileUtil.readFileBytes(inputFile.absolute, 1, offset+3))[0]!==0xB8)
			return false;

		return true;
	};
	converters = ["deark[module:show_gmr][opt:text:encconv=0]"];
}
