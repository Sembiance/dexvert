import {Format} from "../../Format.js";

export class st6CompressedAstrocameraBitmap extends Format
{
	name       = "ST-6 compressed astrocamera bitmap";
	website    = "https://web.archive.org/web/20210610121116/https://hwiegman.home.xs4all.nl/fileformats/sbig/sbig.txt";
	ext        = [".st6"];
	magic      = ["ST-6 compressed astrocamera bitmap"];
	converters = ["nconvert"];
}
