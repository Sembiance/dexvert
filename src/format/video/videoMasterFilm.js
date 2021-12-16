import {Format} from "../../Format.js";

export class videoMasterFilm extends Format
{
	name       = "Video Master Film";
	website    = "http://fileformats.archiveteam.org/wiki/Video_Master_Film";
	ext        = [".flm", ".vid", ".vsq"];
	magic      = ["Video Master Film"];
	converters = ["deark -> *joinAsGIF -> ffmpeg"];
}
