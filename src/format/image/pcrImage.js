import {Format} from "../../Format.js";

export class pcrImage extends Format
{
	name           = "PCR Image";
	website        = "http://fileformats.archiveteam.org/wiki/PCR_image";
	ext            = [".pcr"];
	forbidExtMatch = true;
	magic          = ["PCR Image"];
	unsupported    = true;
}
