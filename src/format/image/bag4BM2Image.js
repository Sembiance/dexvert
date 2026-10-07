import {Format} from "../../Format.js";

export class bag4BM2Image extends Format
{
	name           = "BAG4 BM2 Image";
	ext            = [".bm2"];
	forbidExtMatch = true;
	magic          = [/^geViewer: BAG_4_BM2_BM( |$)/];
	converters     = ["gameextractor[renameOut][codes:BAG_4_BM2_BM]"];
}
