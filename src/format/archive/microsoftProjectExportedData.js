import {Format} from "../../Format.js";

export class microsoftProjectExportedData extends Format
{
	name           = "Microsoft Project exported data";
	ext            = [".mpx"];
	forbidExtMatch = true;
	magic          = ["Microsoft Project exported data", /^Microsoft Project$/, /^fmt\/(342|440)( |$)/, /^x-fmt\/(243|247)( |$)/];
	converters     = ["deark[module:cfb]"];
}
