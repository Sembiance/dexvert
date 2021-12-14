import {Format} from "../../Format.js";

export class animaticFilm extends Format
{
	name       = "Animatic Film";
	website    = "http://fileformats.archiveteam.org/wiki/Animatic_Film";
	ext        = [".flm"];
	magic      = ["Animatic Film"];
	converters = ["deark -> *joinAsGIF -> ffmpeg", "deark"];
}
