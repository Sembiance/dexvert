import {Format} from "../../Format.js";

export class maelstromANM extends Format
{
	name           = "Mailestrom ANM";
	website        = "https://wiki.multimedia.cx/index.php/Maelstrom_ANM";
	ext            = [".anm"];
	forbidExtMatch = true;
	magic          = ["Maeldemo Animation"];
	converters     = ["na_game_tool[format:maelstrom-anm]"];
}
