import {Format} from "../../Format.js";

export class eXoticADLib extends Format
{
	name         = "eXotic AdLib";
	ext          = [".xad"];
	magic        = ["eXotic ADlib", "Exotic AdLib module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
