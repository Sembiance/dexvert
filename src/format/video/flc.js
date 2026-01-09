import {Format} from "../../Format.js";

export class flc extends Format
{
	name         = "FLIC FLC Video";
	website      = "http://fileformats.archiveteam.org/wiki/FLIC";
	ext          = [".flc"];
	magic        = ["FLIC FLC video", "FLC animation", "Autodesk Animator Pro FLIC", "FLI/FLC/FLX animation (flic)", "deark: fli (FLC)", /^fmt\/298( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="FLIC" && macFileCreator==="BABL";
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:flic]", "noesis[type:animated]", "xanim", "deark[module:fli] -> *ffmpeg[fps:15]"];
}
