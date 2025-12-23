import {Format} from "../../Format.js";

export class logitechCompress extends Format
{
	name       = "Logitech Compress Archive";
	magic      = ["Logitech Compress compressed", "deark: lgcompress", /^Logitech Compress archive data/];
	weakMagic  = [/^Logitech Compress archive data/];
	converters = ["deark[module:lgcompress][missingLetter]"];
}
