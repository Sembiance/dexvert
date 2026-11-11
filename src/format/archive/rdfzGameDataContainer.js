import {Format} from "../../Format.js";

export class rdfzGameDataContainer extends Format
{
	name           = "RDFZ game data container";
	magic          = ["RDFZ game data container", /^geArchive: NoExt_RDFZ( |$)/];
	converters     = ["gameextractor[codes:NoExt_RDFZ]"];
}
