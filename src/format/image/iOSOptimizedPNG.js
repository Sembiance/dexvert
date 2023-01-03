import {Format} from "../../Format.js";

export class iOSOptimizedPNG extends Format
{
	name           = "iOS/Apple Optimized PNG";
	ext            = [".png"];
	forbidExtMatch = true;
	magic          = ["iOS optimized PNG bitmap", "Portable Network Graphics (Apple variant)"];
	converters     = ["nconvert"];
}
