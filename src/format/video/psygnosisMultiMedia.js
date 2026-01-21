import {Format} from "../../Format.js";

export class psygnosisMultiMedia extends Format
{
	name           = "Psygnosis MultiMedia Video";
	website        = "https://wiki.multimedia.cx/index.php/PMM";
	ext            = [".pmm"];
	forbidExtMatch = true;
	magic          = ["PMM video"];
	converters     = ["na_game_tool[format:pmm]"];
}
