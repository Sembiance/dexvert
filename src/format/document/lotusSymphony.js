import {Format} from "../../Format.js";

export class lotusSymphony extends Format
{
	name        = "Lotus Symphony Worksheet";
	ext         = [".wk1", ".wr1"];
	magic       = ["Lotus 123/Symphony Worksheet", "Lotus 1-2-3/Symphony worksheet", /^Lotus 1-2-3 worksheet/];
	unsupported = true;
}
