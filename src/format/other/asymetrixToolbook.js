
import {Format} from "../../Format.js";

export class asymetrixToolbook extends Format
{
	name           = "Asymetrix ToolBook File";
	website        = "http://fileformats.archiveteam.org/wiki/Asymetrix_Toolbook";
	ext            = [".tbk", ".sbk"];
	forbidExtMatch = true;
	magic          = ["Asymetrix ToolBook", /^fmt\/470( |$)/];
	converters     = ["strings"];
}
