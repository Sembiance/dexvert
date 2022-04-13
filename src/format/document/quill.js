import {Format} from "../../Format.js";

export class quill extends Format
{
	name           = "Quill Document";
	website        = "http://www.rwapadventures.com/ql_wiki/index.php?title=Quill";
	ext            = [".doc"];
	forbidExtMatch = true;
	magic          = ["Quill Document"];
	converters     = ["strings"];
}
