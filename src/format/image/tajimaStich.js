import {xu} from "xu";
import {Format} from "../../Format.js";

export class tajimaStich extends Format
{
	name           = "Tajima Stitch";
	ext            = [".dst"];
	forbidExtMatch = true;
	magic          = ["Tajima stitch image"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="TAJI" && macFileCreator==="3dVE";
	converters     = ["konvertor"];
}
