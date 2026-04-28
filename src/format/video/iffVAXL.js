import {Format} from "../../Format.js";

export class iffVAXL extends Format
{
	name       = "Optonica Videostream VAXL";
	website    = "http://fileformats.archiveteam.org/wiki/VAXL";
	ext        = [".vaxl"];
	magic      = ["Optonica Videostream VAXL video"];
	converters = ["vibe2avi"];
}
