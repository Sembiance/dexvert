import {Format} from "../../Format.js";

export class quake2Cinematic extends Format
{
	name         = "Quake II Cinematic Video";
	website      = "https://multimedia.cx/mirror/idcin.html";
	ext          = [".cin"];
	weakExt      = true;
	magic        = ["Id Software Quake II Cinematic video", "id Cinematic (idcin)"];
	trustMagic   = true;
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:idcin]"];
}
