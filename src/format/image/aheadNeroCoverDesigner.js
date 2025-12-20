import {Format} from "../../Format.js";

export class aheadNeroCoverDesigner extends Format
{
	name           = "Ahead Nero CoverDesigner";
	ext            = [".nct", ".bcd"];
	forbidExtMatch = true;
	magic          = ["Ahead Nero CoverDesigner", "CoverDesigner template :cnc[dt]:", "Nero CoverDesigner", /^fmt\/1368( |$)/];
	converters     = ["nconvert[format:cnct]"];
}
