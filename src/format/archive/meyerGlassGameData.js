import {Format} from "../../Format.js";

export class meyerGlassGameData extends Format
{
	name           = "Meyer/Glass Interactive Game Data";
	ext            = [".mgf"];
	forbidExtMatch = true;
	magic          = ["Meyer/Glass Interactive game data Format"];
	converters     = ["gameextractor"];
}
