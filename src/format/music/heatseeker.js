import {xu} from "xu";
import {Format} from "../../Format.js";

export class heatseeker extends Format
{
	name         = "Heatseeker Module";
	ext          = [".hmc", ".crb"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
