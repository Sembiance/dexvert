import {xu} from "xu";
import {Format} from "../../Format.js";

export class ascSoundMaster extends Format
{
	name         = "ASC Sound Master";
	ext          = [".asc"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];

	// Because we just have an extension, sometimes ASCII files will convert and end up being just garbage. So ensure we have at least a 0.33 second long music file result
	verify = ({meta}) => meta.duration>=xu.SECOND/3;
}
