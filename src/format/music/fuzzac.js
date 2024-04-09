import {xu} from "xu";
import {Format} from "../../Format.js";

export class fuzzac extends Format
{
	name         = "Fuzzac Packer Module";
	ext          = [".fuzzac"];
	metaProvider = ["musicInfo"];
	priority     = this.PRIORITY.LOWEST;
	converters   = ["uade123", "xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
