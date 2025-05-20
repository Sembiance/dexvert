
import {Format} from "../../Format.js";

export class gameMusicFormat extends Format
{
	name           = "Game Music Format";
	website        = "https://www.vgmpf.com/Wiki/index.php?title=GMF";
	ext            = [".gmf"];
	forbidExtMatch = true;
	magic          = ["Game Music Format"];
	converters     = ["midistar2mp3"];
}
