import {Format} from "../../Format.js";

export class faxMan extends Format
{
	name           = "FaxManager/FaxMan/FaxWizard";
	website        = "http://fileformats.archiveteam.org/wiki/FaxManager";
	ext            = [".fmf"];
	forbidExtMatch = true;
	magic          = ["Fax man :fmf:", "FaxMan/ImageMan image"];
	converters     = ["nconvert[format:fmf]"];
}
