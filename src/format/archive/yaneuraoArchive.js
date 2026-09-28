import {Format} from "../../Format.js";

export class yaneuraoArchive extends Format
{
	name           = "Yaneurao Archive";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["archive:Yaneurao.PackOpener", "archive:Yaneurao.PackExOpener"];
	converters     = ["GARbro[types:archive:Yaneurao.PackExOpener,archive:Yaneurao.PackOpener]"];
}
