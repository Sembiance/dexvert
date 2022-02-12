import {Format} from "../../Format.js";

export class jbmAdLib extends Format
{
	name         = "JBM AdLib";
	ext          = [".jbm"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
