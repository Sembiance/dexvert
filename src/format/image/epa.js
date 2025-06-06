import {Format} from "../../Format.js";

export class epa extends Format
{
	name           = "Award BIOS Logo";
	website        = "http://fileformats.archiveteam.org/wiki/Award_BIOS_logo";
	ext            = [".epa"];
	forbidExtMatch = true;
	magic          = ["deark: awbm (Award BIOS logo", "Award Bios Logo :epa:", /^Award BIOS [Ll]ogo/];
	weakMagic      = true;

	// nconvert, as usual, messes up several files
	converters     = ["recoil2png", "deark[module:awbm]", "nconvert[format:epa]"];
}
