import {xu} from "xu";
import {Format} from "../../Format.js";

export class cDilla extends Format
{
	name       = "C-DILLA Packed File";
	magic      = ["C-DILLA Packed File"];
	packed     = true;
	converters = ["vibeExtract"];
}
