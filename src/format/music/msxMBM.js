import {Format} from "../../Format.js";

export class msxMBM extends Format
{
	name        = "MSX Moon Blaster Music";
	ext         = [".mbm"];
	unsupported = true;
	converters  = ["kss2wav"];
	notes       = "Conversion works great, but kss2wav will take almost any .mbm file and convert it to garbage. No magic I can find and no current way to check output audio, so since the format is so rare, sadly need to mark it unsupported.";
}
