import {xu} from "xu";
import {Format} from "../../Format.js";

export class zenPacker extends Format
{
	name         = "Zen Packer Module";
	ext          = [".zen"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
