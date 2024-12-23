import {Format} from "../../Format.js";

export class esmSoftwarePIX extends Format
{
	name           = "Esm Software PIX Image";
	website        = "http://fileformats.archiveteam.org/wiki/Esm_Software_PIX";
	ext            = [".pix"];
	forbidExtMatch = [".pix"];
	magic          = ["Esm Software PIX bitmap"];
	converters     = ["nconvert"];
}
