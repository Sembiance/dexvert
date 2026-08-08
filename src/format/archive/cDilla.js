import {xu} from "xu";
import {Format} from "../../Format.js";

export class cDilla extends Format
{
	name       = "C-DILLA Packed File";
	magic      = ["C-DILLA Packed File", "C-Dilla protected"];
	packed     = true;
	converters = ["vibeExtract"];
}
