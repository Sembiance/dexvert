import {Format} from "../../Format.js";

export class trs80Clp extends Format
{
	name       = "TRS-80 CLP File";
	ext        = [".clp"];
	converters = ["wuimg[format:trs80clp]", "recoil2png[format:CLP.CocoClp]"];
}
