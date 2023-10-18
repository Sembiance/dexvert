import {Format} from "../../Format.js";

export class fli extends Format
{
	name         = "FLIC FLI Video";
	website      = "http://fileformats.archiveteam.org/wiki/FLIC";
	ext          = [".fli"];
	magic        = ["FLIC FLI video", "FLI animation", "AutoDesk FLIC Animation", /^x-fmt\/(154|299)( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:flic]", "xanim", "deark[module:fli] -> *ffmpeg[fps:15]"];
}
