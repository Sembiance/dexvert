import {Format} from "../../Format.js";

export class sonicArranger extends Format
{
	name         = "Sonic Arrange Module";
	ext          = [".sa"];
	magic        = ["Sonic Arranger module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
