import {Format} from "../../Format.js";

export class iffVAXL extends Format
{
	name        = "Optonica Videostream VAXL";
	website     = "http://fileformats.archiveteam.org/wiki/VAXL";
	ext         = [".vaxl"];
	magic       = ["Optonica Videostream VAXL video"];
	unsupported = true;
	notes       = "Could only find this potential viewer, but no download link: https://www.ultimateamiga.com/index.php?topic=9605.0";
}
