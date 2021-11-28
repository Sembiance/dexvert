import {Format} from "../../Format.js";

export class threeDCK extends Format
{
	name           = "3D Construction Kit";
	ext            = [".run"];
	forbidExtMatch = true;
	magic          = ["3D Construction Kit game Runner"];
	website        = "https://en.wikipedia.org/wiki/3D_Construction_Kit";
	converters     = ["runvga"];
}
