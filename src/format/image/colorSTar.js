import {Format} from "../../Format.js";

export class colorSTar extends Format
{
	name       = "ColorSTar/MonoSTar";
	ext        = [".bil", ".obj"];
	converters = ["recoil2png[format:OBJ,BIL]"];
}
