import {Format} from "../../Format.js";

export class softimageXSI extends Format
{
	name           = "Softimage XSI";
	website        = "http://fileformats.archiveteam.org/wiki/DotXSI";
	ext            = [".xsi"];
	forbidExtMatch = true;
	magic          = ["SoftImage XSI 3D image"];
	converters     = ["threeDObjectConverter[outType:wavefrontOBJ]"];	// could not get to work: "AccuTrans3D", "milkShape3D[format:softimageXSI]"
}
