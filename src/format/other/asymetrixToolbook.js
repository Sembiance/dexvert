
import {Format} from "../../Format.js";

export class asymetrixToolbook extends Format
{
	name           = "Asymetrix ToolBook File";
	ext            = [".tbk"];
	forbidExtMatch = true;
	magic          = ["Asymetrix ToolBook", /^fmt\/470( |$)/];
	converters     = ["strings"];
}
