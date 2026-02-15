import {Format} from "../../Format.js";

export class oricFont extends Format
{
	name       = "Oric Font";
	ext        = [".chs"];
	magic      = ["Oric Tape image"];	// This isn't really magic for this file, haven't identified any real magic yet, and .chs is too generic for recoil
	weakMagic  = true;
	converters = ["recoil2png[format:CHS]"];
}
