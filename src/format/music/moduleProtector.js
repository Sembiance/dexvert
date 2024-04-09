import {xu} from "xu";
import {Format} from "../../Format.js";

export class moduleProtector extends Format
{
	name         = "Module Protector Module";
	ext          = [".mp"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
