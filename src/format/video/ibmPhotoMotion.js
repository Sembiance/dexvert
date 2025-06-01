import {Format} from "../../Format.js";

export class ibmPhotoMotion extends Format
{
	name         = "IBM PhotoMotion MM Video";
	website      = "https://wiki.multimedia.cx/index.php/IBM_PhotoMotion";
	ext          = [".mm"];
	magic        = ["American Laser Games MM video", "American Laser Games MM (mm)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:mm]"];
	verify       = ({meta}) => (meta.duration || 0)>=1000;	// ensure a duration of at least 1 second, otherwise it's not likely a valid video file
}
