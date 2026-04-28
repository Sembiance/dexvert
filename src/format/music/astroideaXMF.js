import {Format} from "../../Format.js";

export class astroideaXMF extends Format
{
	name         = "Astroidea XMF";
	ext          = [".xmf"];
	metaProvider = ["musicInfo"];
	converters   = ["openmpt123"]
}
