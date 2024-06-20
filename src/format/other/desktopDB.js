import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class desktopDB extends Format
{
	name        = "Desktop DB";
	filename    = [/^desktop db$/i];
	idCheck     = async inputFile => inputFile.size>=512 && (await fileUtil.readFileBytes(inputFile.absolute, 8, 504)).indexOfX([0x01, 0xF8, 0x00, 0xF8, 0x00, 0x78, 0x00, 0x0E])===0;
	idMeta      = ({macFileType, macFileCreator}) => macFileType==="BTFL" && macFileCreator==="DMGR";
	unsupported = true;
}
