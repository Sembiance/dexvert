import {Format} from "../../Format.js";

export class lightscapePreparatation extends Format
{
	name       = "Lightscape Preparatation";
	ext        = [".lp"];
	magic      = ["Lightscape Preparatation"];
	converters = ["AccuTrans3D", "threeDObjectConverter"];
}
