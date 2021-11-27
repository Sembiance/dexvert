import {Format} from "../../Format.js";

export class hir extends Format
{
	name       = "Print-Technik HIR Image";
	ext        = [".hir"];
	magic      = ["Print-Technik/PRO89xx Raw data bitmap"];
	converters = ["recoil2png"]
}
