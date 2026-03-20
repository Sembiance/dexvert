import {Format} from "../../Format.js";

export class yaneuraoArchive extends Format
{
	name           = "Yaneurao Archive";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["archive:Yaneurao.PackOpener"];
	converters     = ["GARbro[types:archive:Yaneurao.PackOpener]"];
}
