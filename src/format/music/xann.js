import {xu} from "xu";
import {Format} from "../../Format.js";

export class xann extends Format
{
	name         = "Xann Packer Module";
	ext          = [".xann"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
