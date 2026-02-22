import {Format} from "../../Format.js";

export class logitechCompress extends Format
{
	name       = "Logitech Compress Archive";
	magic      = ["Logitech Compress compressed", "deark: lgcompress", /^Logitech Compress archive data/, /^idarc: Logitech Compress( |$)/];
	weakMagic  = [/^Logitech Compress archive data/];
	converters = ["deark[module:lgcompress][missingLetter]"];
}
