import {Format} from "../../Format.js";

export class fli extends Format
{
	name         = "FLIC FLI Video";
	website      = "http://fileformats.archiveteam.org/wiki/FLIC";
	ext          = [".fli"];
	magic        = ["FLIC FLI video", "FLI animation", "AutoDesk FLIC Animation", "Autodesk Animator", "FLI/FLC/FLX animation (flic)", /^x-fmt\/154( |$)/, /^fmt\/(299)( |$)/];
	idMeta       = ({macFileType}) => ["pFLI", "FLI "].includes(macFileType);
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:flic]", "xanim", "deark[module:fli] -> *ffmpeg[fps:15]"];
}
