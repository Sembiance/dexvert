import {Format} from "../../Format.js";

export class sgsDAT extends Format
{
	name       = "SGS.DAT File";
	filename   = [/^sgs.dat$/i];
	magic      = ["SGS.DAT"];
	converters = ["decomposeSGS"];
}
