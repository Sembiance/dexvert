import {Format} from "../../Format.js";

export class faxMan extends Format
{
	name           = "FaxMan";
	ext            = [".fmf"];
	forbidExtMatch = true;
	magic          = ["Fax man :fmf:"];
	converters     = ["nconvert[format:fmf]"];
}
