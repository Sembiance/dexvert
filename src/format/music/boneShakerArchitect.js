import {Format} from "../../Format.js";

export class boneShakerArchitect extends Format
{
	name       = "The Bone Sahker Architect";
	website    = "https://vgmpf.com/Wiki/index.php?title=TBSA";
	ext        = [".tbs", ".bsa"];
	magic      = ["The Bone Shaker Architect music"];
	converters = ["gamemus[format:tbsa-doofus]"];
}
