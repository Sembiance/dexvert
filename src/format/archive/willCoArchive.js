import {Format} from "../../Format.js";

export class willCoArchive extends Format
{
	name           = "Will Co. Game Archive";
	ext            = [".arc"];
	forbidExtMatch = true;
	magic          = ["archive:Will.ArcOpener"];
	converters     = ["GARbro[types:archive:Will.ArcOpener]"];
}
