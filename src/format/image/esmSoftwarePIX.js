import {Format} from "../../Format.js";

export class esmSoftwarePIX extends Format
{
	name           = "Esm Software PIX Image";
	website        = "http://fileformats.archiveteam.org/wiki/Esm_Software_PIX";
	ext            = [".pix"];
	forbidExtMatch = [".pix"];
	magic          = ["Esm Software PIX bitmap", "deark: esm_pix"];
	converters     = ["deark[module:esm_pix]"];
}
