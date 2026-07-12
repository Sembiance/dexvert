import {Format} from "../../Format.js";

export class mszp extends Format
{
	name       = "MSZP Compressed File";
	magic      = ["MSZP Compressed File"];
	packed     = true;
	converters = ["vibeExtract"];
}
