import {Format} from "../../Format.js";

export class h2oGameDataArchive extends Format
{
	name           = "Liquid Entertainment H2O game data archive";
	ext            = [".h2o"];
	forbidExtMatch = true;
	magic          = ["Liquid Entertainment H2O game data archive", /^geArchive: H2O_2( |$)/];
	converters     = ["gameextractor[codes:H2O_2]"];
}
