import {Format} from "../../Format.js";

export class hscAdLibComposer extends Format
{
	name         = "HSC AdLib Composer";
	ext          = [".hsc"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
