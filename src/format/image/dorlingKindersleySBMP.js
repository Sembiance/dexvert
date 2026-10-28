import {Format} from "../../Format.js";

export class dorlingKindersleySBMP extends Format
{
	name           = "Dorling Kindersley SBMP";
	ext            = [".sbm"];
	forbidExtMatch = true;
	magic          = ["Dorling Kindersley SBMP", "Generic RIFF file SBMP"];
	converters     = ["na_eofdec[format:sbmp][outType:bmp]"];
}
