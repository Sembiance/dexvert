import {xu} from "xu";
import {Format} from "../../Format.js";

export class desktopDF extends Format
{
	name        = "Desktop DF";
	filename    = [/^desktop df$/i];
	idMeta      = ({macFileType, macFileCreator}) => macFileType==="DTFL" && macFileCreator==="DMGR";
	unsupported = true;
}
