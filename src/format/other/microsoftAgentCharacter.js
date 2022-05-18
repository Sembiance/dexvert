import {Format} from "../../Format.js";

export class microsoftAgentCharacter extends Format
{
	name           = "Microsoft Agent Character";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Agent_character";
	ext            = [".acs", ".acf", ".aca"];
	forbidExtMatch = true;
	magic          = ["Microsoft Agent Character"];
	unsupported    = true;
}
