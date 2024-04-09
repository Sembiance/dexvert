import {xu} from "xu";
import {Format} from "../../Format.js";

export class proPacker extends Format
{
	name         = "ProPacker Module";
	ext          = [".p10", ".pp10", ".p21", ".pp21", ".p30", ".pp30"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
