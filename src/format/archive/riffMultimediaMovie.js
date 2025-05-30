import {Format} from "../../Format.js";

export class riffMultimediaMovie extends Format
{
	name       = "RIFF Multimedia Movie";
	website    = "http://fileformats.archiveteam.org/wiki/RIFF_Multimedia_Movie";
	ext        = [".mmm"];
	magic      = ["MultiMedia Movie format video", "RIFF Datei: unbekannter Typ 'RMMP'", "Generic RIFF file RMMP", /RIFF .*multimedia movie$/, "deark: mmm"];
	converters = ["unMMM & deark[module:mmm]"];
}
