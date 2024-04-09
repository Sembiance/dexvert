import {xu} from "xu";
import {Format} from "../../Format.js";

export class noisePacker extends Format
{
	name         = "NoisePacker Module";
	ext          = [".np1", ".np2", "np3"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
