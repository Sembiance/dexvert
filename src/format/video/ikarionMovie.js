import {Format} from "../../Format.js";

export class ikarionMovie extends Format
{
	name           = "Ikarion Movie";
	ext            = [".mvi"];
	forbidExtMatch = true;
	magic          = ["Ikarion Movie (VR6MVI)", "Ikarion Movie (MVI2)"];
	converters     = dexState => [`na_game_tool[format:mvi${dexState.hasMagics("Ikarion Movie (MVI2)") ? "2" : "1"}]`];
}

