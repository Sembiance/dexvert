import {Format} from "../../Format.js";

export class fli extends Format
{
	name         = "FLIC FLI Video";
	website      = "http://fileformats.archiveteam.org/wiki/FLIC";
	ext          = [".fli"];
	magic        = ["FLIC FLI video", "FLI animation", "AutoDesk FLIC Animation"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:flic]", "xanim"];
}
