import {Format} from "../../Format.js";

export class necEBD extends Format
{
	name       = "NEC PC-98 EBD";
	ext        = [".ebd"];
	converters = ["recoil2png[format:EBD]"];
}
