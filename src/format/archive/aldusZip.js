import {Format} from "../../Format.js";

export class aldusZip extends Format
{
	name       = "Aldus Zip Compressed File";
	magic      = ["Aldus Zip compressed installation data"];
	converters = ["deark[module:aldus_inst]"];
}
