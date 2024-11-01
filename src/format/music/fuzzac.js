import {xu} from "xu";
import {Format} from "../../Format.js";

export class fuzzac extends Format
{
	name         = "Fuzzac Packer Module";
	website      = "http://fileformats.archiveteam.org/wiki/Fuzzac_Packer_module";
	ext          = [".fuzzac"];
	magic        = ["Fuzzac Packer module"];
	metaProvider = ["musicInfo"];
	priority     = this.PRIORITY.LOWEST;
	converters   = ["uade123", "xmp"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
