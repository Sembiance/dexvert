import {Format} from "../../Format.js";

export class activeMime extends Format
{
	name           = "ActiveMime";
	website        = "http://fileformats.archiveteam.org/wiki/ActiveMime";
	ext            = [".mso"];
	forbidExtMatch = true;
	magic          = ["ActiveMime"];
	converters     = ["activeMimeExtractor"];
}
