import {Format} from "../../Format.js";

export class eci extends Format
{
	name       = "ECI Graphic Editor";
	website    = "http://fileformats.archiveteam.org/wiki/ECI_Graphic_Editor";
	ext        = [".eci", ".ecp"];
	converters = ["recoil2png", "view64"];
}
