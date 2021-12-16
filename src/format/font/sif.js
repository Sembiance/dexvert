import {Format} from "../../Format.js";

export class sif extends Format
{
	name       = "Super-IRG";
	ext        = [".sif"];
	fileSize   = 2048;
	converters = ["recoil2png"];
}
