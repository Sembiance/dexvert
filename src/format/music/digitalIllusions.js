import {xu} from "xu";
import {Format} from "../../Format.js";

export class digitalIllusions extends Format
{
	name         = "Digital Illusions Module";
	ext          = [".di"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
