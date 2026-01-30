import {Format} from "../../Format.js";

export class hir extends Format
{
	name       = "Print-Technik HIR Image";
	website    = "http://fileformats.archiveteam.org/wiki/Print-Technik";
	ext        = [".hir"];
	magic      = ["Print-Technik/PRO89xx Raw data bitmap"];
	converters = ["recoil2png", "wuimg[format:hir]"];
}
