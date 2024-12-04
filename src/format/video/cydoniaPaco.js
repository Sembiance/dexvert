import {xu} from "xu";
import {Format} from "../../Format.js";

export class cydoniaPaco extends Format
{
	name           = "Cydonia Paco Video";
	website        = "https://wiki.multimedia.cx/index.php/Cydonia_Paco";
	ext            = [".pac"];
	forbidExtMatch = true;
	magic          = ["Cydonia game video format"];
	converters     = ["na_game_tool[format:cydonia]"];
}
