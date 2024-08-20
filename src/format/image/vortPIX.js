import {Format} from "../../Format.js";

export class vortPIX extends Format
{
	name           = "Very Ordinary Rendering Toolkit PIX";
	website        = "http://fileformats.archiveteam.org/wiki/VORT_file";
	ext            = [".vort", ".pix"];
	forbidExtMatch = [".pix"];
	magic          = ["Very Ordinary Raster file format bitmap"];
	converters     = ["deark[module:vort]"];
}
