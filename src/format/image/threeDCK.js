import {Format} from "../../Format.js";

export class threeDCK extends Format
{
	name           = "3D Construction Kit";
	website        = "http://fileformats.archiveteam.org/wiki/3D_Construction_Kit";
	ext            = [".run"];
	forbidExtMatch = true;
	magic          = ["3D Construction Kit game Runner"];
	converters     = ["runvga"];
}
