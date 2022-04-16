import {Format} from "../../Format.js";

export class psionWVE extends Format
{
	name         = "Psion WVE Audio";
	website      = "http://fileformats.archiveteam.org/wiki/WVE_(Psion)";
	ext          = [".wve", ".sdn"];
	magic        = ["Psion Series 3 audio"];
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[outType:mp3]", "awaveStudio"];
}
