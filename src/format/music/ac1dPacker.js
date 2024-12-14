import {Format} from "../../Format.js";

export class ac1dPacker extends Format
{
	name         = "AC1D Packer Module";
	website      = "http://fileformats.archiveteam.org/wiki/AC1D-DC1A_Packer";
	ext          = [".ac1d", ".ac1"];
	magic        = ["AC1D-DC1A Packer"];
	metaProvider = ["muscInfo"];
	converters   = ["uade123", "xmp"];
}
