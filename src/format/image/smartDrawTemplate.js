import {Format} from "../../Format.js";

export class smartDrawTemplate extends Format
{
	name           = "SmartDraw Template";
	ext            = [".sdt", ".sdr"];
	forbidExtMatch = true;
	magic          = ["SmartDraw template", /^fmt\/623( |$)/, "SmartDraw 6 template :sdt:"];
	converters     = ["nconvert[format:sdt]"];
}
