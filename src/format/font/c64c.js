import {Format} from "../../Format.js";

export class c64c extends Format
{
	name       = "C64 8x8 Font";
	ext        = [".64c"];
	magic      = ["C64 8x8 font bitmap"];
	weakMagic  = true;
	converters = ["recoil2png[format:64C]"];
}
