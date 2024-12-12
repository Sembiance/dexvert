import {Format} from "../../Format.js";

export class ibmPhotoMotion extends Format
{
	name         = "IBM PhotoMotion MM Video";
	website      = "https://wiki.multimedia.cx/index.php/IBM_PhotoMotion";
	ext          = [".mm"];
	magic        = ["American Laser Games MM video", "American Laser Games MM (mm)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:mm]"];
}
