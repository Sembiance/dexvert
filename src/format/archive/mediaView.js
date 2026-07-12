import {Format} from "../../Format.js";

export class mediaView extends Format
{
	name           = "Microsoft MediaView";
	ext            = [".m20", ".m21", ".m22", ".m53", ".ybk", ".ivt"];
	forbidExtMatch = true;
	magic          = ["Microsoft MediaView"];
	converters     = ["vibeExtract"];
}
