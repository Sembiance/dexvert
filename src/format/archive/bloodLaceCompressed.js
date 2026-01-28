import {Format} from "../../Format.js";

export class bloodLaceCompressed extends Format
{
	name       = "Blood & Lace Compressed";
	magic      = [/^Blood & Lace Compressed$/];
	converters = ["bl_unpack"];
}
