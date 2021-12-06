import {Format} from "../../Format.js";

export class musiclineModule extends Format
{
	name         = "Musicline Module";
	website      = "https://www.musicline.org/";
	ext          = [".ml"];
	magic        = ["Musicline module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:MusiclineEditor]"];
}
