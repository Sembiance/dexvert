import {Format} from "../../Format.js";

export class willCoWIPArchive extends Format
{
	name           = "Will Co. WIP Archive";
	ext            = [".wip"];
	forbidExtMatch = true;
	magic          = ["archive:Will.WipOpener", "image:Will.WipFormat"];
	converters     = ["GARbro[types:image:Will.WipFormat,archive:Will.WipOpener]"];
}
