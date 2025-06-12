import {Format} from "../../Format.js";

export class aheadNeroCoverDesignerTemplate extends Format
{
	name           = "Ahead Nero CoverDesigner Template";
	ext            = [".nct"];
	forbidExtMatch = true;
	magic          = ["Ahead Nero CoverDesigner Template", "CoverDesigner template :cnct:"];
	converters     = ["nconvert[format:cnct]"];
}
