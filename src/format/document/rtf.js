import {Format} from "../../Format.js";

export class rtf extends Format
{
	name           = "Rich Text Format";
	website        = "http://fileformats.archiveteam.org/wiki/RTF";
	ext            = [".rtf"];
	forbidExtMatch = true;
	magic          = ["Rich Text Format", "Format: RTF", "Marcel document", /^fmt\/(45|50|52|53|355|969)( |$)/];
	idMeta         = ({macFileType}) => macFileType==="RTF ";

	// fileMerlin will convert RTF too, but it produces artifacts (page 30, 31, etc in document/rtf/DIGITIZE.RTF)
	converters     = ["soffice[format:Rich Text Format]", "soffice[format:Rich Text Format StarCalc]"];
}
