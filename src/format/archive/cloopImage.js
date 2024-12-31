import {Format} from "../../Format.js";

export class cloopImage extends Format
{
	name       = "cloop Image";
	magic      = [/^Linux cloop .*image/];
	converters = ["extractCompressedFS"];
}
