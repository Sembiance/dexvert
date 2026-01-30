import {Format} from "../../Format.js";

export class signumBitmap extends Format
{
	name           = "Signum! bitmap";
	website        = "http://justsolve.archiveteam.org/wiki/Signum!_Compressed_Image_(IMC)";
	ext            = [".imc", ".pac"];
	forbidExtMatch = true;
	magic          = ["Signum! bitmap"];
	converters     = ["wuimg[format:imc]"];
}
