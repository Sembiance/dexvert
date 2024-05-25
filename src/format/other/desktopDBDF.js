import {xu} from "xu";
import {Format} from "../../Format.js";

export class desktopDBDF extends Format
{
	name        = "Desktop DB/DF";
	filename    = [/^desktop d[bf]$/i];
	idMeta      = ({macFileType, macFileCreator}) => ["BTFL", "DTFL"].includes(macFileType) && macFileCreator==="DMGR";
	unsupported = true;
}
