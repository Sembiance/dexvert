import {Format} from "../../Format.js";

export class flc extends Format
{
	name         = "FLIC FLC Video";
	website      = "http://fileformats.archiveteam.org/wiki/FLIC";
	ext          = [".flc"];
	magic        = ["FLIC FLC video", "FLC animation", "Autodesk Animator Pro FLIC", /^fmt\/298( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:flic]", "xanim", "deark[module:fli] -> *ffmpeg[fps:15]"];
}
