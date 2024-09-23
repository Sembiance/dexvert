import {Format} from "../../Format.js";

export class rtf extends Format
{
	name           = "Rich Text Format";
	website        = "http://fileformats.archiveteam.org/wiki/RTF";
	ext            = [".rtf"];
	forbidExtMatch = true;
	magic          = ["Rich Text Format", "Format: RTF", "Marcel document", "application/rtf", /^fmt\/(45|50|52|53|355|969)( |$)/];
	idMeta         = ({macFileType}) => macFileType==="RTF ";

	// fileMerlin will convert RTF too, but it produces artifacts (page 30, 31, etc in document/rtf/DIGITIZE.RTF)
	converters     = [
		// handles most RTF files
		"soffice[format:Rich Text Format]", "soffice[format:Rich Text Format StarCalc]",
		
		// handles tricky ones like EOExpressionContext.rtf
		"fileMerlin[matchType:magic][hasExtMatch]",
		
		// handles really tricky ones like 1368_printer_voice_alerts.rtf
		"wordForWord[matchType:magic][hasExtMatch]"	// this actually outputs RTF, but it can open badly formed RTF files and output good ones that soffice can handle
	];
}
