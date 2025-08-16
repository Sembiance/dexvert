import {Format} from "../../Format.js";

export class trs80Clp extends Format
{
	name       = "TRS-80 CLP File";
	ext        = [".clp"];
	converters = ["recoil2png", "wuimg"];
}
