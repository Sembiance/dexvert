import {Format} from "../../Format.js";

export class skytPacker extends Format
{
	name         = "SKYT/Drifters Packer";
	ext          = [".skyt"];
	magic        = ["SKYT/Drifters Packer song"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
}
