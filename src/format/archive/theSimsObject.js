import {Format} from "../../Format.js";

export class theSimsObject extends Format
{
	name           = `"The Sims" object`;
	ext            = [".flr", ".wll", ".iff"];
	forbidExtMatch = true;
	magic          = [`"The Sims" object`, /^geArchive: IFF( |$)/];
	converters     = ["gameextractor[codes:IFF]"];
}
