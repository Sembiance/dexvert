import {xu} from "xu";
import {Format} from "../../Format.js";

export class asymetrixToolbook extends Format
{
	name           = "Asymetrix ToolBook File";
	website        = "http://fileformats.archiveteam.org/wiki/Asymetrix_Toolbook";
	ext            = [".tbk", ".sbk"];
	forbidExtMatch = true;
	magic          = ["Asymetrix ToolBook", "Asymetrix data (generic)", /^fmt\/(470|1795)( |$)/];
	converters     = ["vibeExtract", "strings"];	// vibe converter not complete, but good enough for now
}
