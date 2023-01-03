import {Format} from "../../Format.js";

export class thunderCompressed extends Format
{
	name           = "Thunder Compressed File";
	ext            = [".jpm"];
	forbidExtMatch = true;
	magic          = ["Thunder compressed data"];
	packed         = true;
	converters     = ["xfdDecrunch"];
}
