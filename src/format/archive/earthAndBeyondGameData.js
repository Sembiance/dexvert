import {Format} from "../../Format.js";

export class earthAndBeyondGameData extends Format
{
	name           = "Earth and Beyond Game Data Archive";
	ext            = [".mix"];
	forbidExtMatch = true;
	magic          = ["Earth And Beyond game data archive"];
	converters     = ["gameextractor"];
}
