import {Format} from "../../Format.js";

export class psionWVE extends Format
{
	name         = "Psion WVE Audio";
	website      = "http://fileformats.archiveteam.org/wiki/WVE_(Psion)";
	ext          = [".wve", ".sdn"];
	magic        = ["Psion Series 3 audio", /^soxi: wve$/, "Psion 3 ALaw audio (wve)"];
	metaProvider = ["soxi"];
	converters   = ["sox[type:wve]", "ffmpeg[format:wve][outType:mp3]", "awaveStudio[matchType:magic]"];
}
