import {Format} from "../../Format.js";

export class psygnosisYOP extends Format
{
	name         = "Psygnosis YOP Video";
	website      = "https://wiki.multimedia.cx/index.php/Psygnosis_YOP";
	ext          = [".yop"];
	magic        = ["Psygnosis YOP video"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
