import {Format} from "../../Format.js";

export class ac1dPacker extends Format
{
	name         = "AC1D Packer Module";
	ext          = [".ac1d", ".ac1"];
	metaProvider = ["muscInfo"];
	converters   = ["uade123", "xmp"];
}
