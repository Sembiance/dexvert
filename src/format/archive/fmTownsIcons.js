import {Format} from "../../Format.js";

export class fmTownsIcons extends Format
{
	name       = "FM-Towns Icons Archive";
	ext        = [".icn"];
	magic      = ["Towns OS Icon (ICNFILE)"];
	converters = ["deark[module:fmtowns_icn]"];
}
