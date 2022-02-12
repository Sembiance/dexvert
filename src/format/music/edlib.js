import {Format} from "../../Format.js";

export class edlib extends Format
{
	name         = "Edlib";
	ext          = [".d00"];
	magic        = ["EdLib module", /^EdLib$/, "EdLib packed module"];
	notes        = "Packed .edl and .d01 modules not supported.";
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
