import {Format} from "../../Format.js";

export class graspFont extends Format
{
	name           = "GRASP Font";
	website        = "http://fileformats.archiveteam.org/wiki/GRASP_font";
	ext            = [".fnt", ".set"];
	forbidExtMatch = true;
	magic          = ["deark: graspfont (GRASP font"];
	converters     = ["deark[module:graspfont]"];
}
