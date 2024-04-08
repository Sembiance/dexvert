import {Format} from "../../Format.js";

export class wantonPacker extends Format
{
	name         = "Wanton Packer Module";
	ext          = [".wn"];
	magic        = ["Wanton Packer song/module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp"];
}
