import {Format} from "../../Format.js";

export class odFontEditor extends Format
{
	name        = "OD Font Editor";
	ext         = [".odf"];
	unsupported = true;
	notes       = "Just have an extension and never encountered one of these files 'in the wild' and recoil will convert things that are not an OD Font file into a garbage image.";
	converters  = ["recoil2png"];
}
