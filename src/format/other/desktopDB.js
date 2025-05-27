import {xu} from "xu";
import {Format} from "../../Format.js";

export class desktopDB extends Format
{
	name        = "Desktop DB";
	filename    = [/^desktop db$/i];
	byteCheck   = [{offset : 504, match : [0x01, 0xF8, 0x00, 0xF8, 0x00, 0x78, 0x00, 0x0E]}];
	idMeta      = ({macFileType, macFileCreator}) => macFileType==="BTFL" && macFileCreator==="DMGR";
	unsupported = true;
}
