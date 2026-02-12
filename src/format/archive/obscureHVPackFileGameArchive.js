import {Format} from "../../Format.js";

export class obscureHVPackFileGameArchive extends Format
{
	name           = "Obscure HV PackFile game archive";
	ext            = [".hvp", ".001"];
	forbidExtMatch = true;
	magic          = ["Obscure HV PackFile game data archive", /^geArchive: HVP_HVPACKFILE( |$)/];
	converters     = ["gameextractor[codes:HVP_HVPACKFILE]"];
}
