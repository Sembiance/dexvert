import {Format} from "../../Format.js";

export class fmTownsIcons extends Format
{
	name       = "FM-Towns Icons";
	ext        = [".icn"];
	magic      = ["Towns OS Icon (ICNFILE)"];
	converters = ["deark[module:fmtowns_icn]"];
}
