import {xu} from "xu";
import {Format} from "../../Format.js";

export class phaPacker extends Format
{
	name         = "Pha Packer Module";
	ext          = [".pha"];
	magic        = ["Pha Packer"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
}
