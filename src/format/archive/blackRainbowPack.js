import {Format} from "../../Format.js";

export class blackRainbowPack extends Format
{
	name           = "Black Rainbow PACK Archive";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = ["archive:BlackRainbow.PackOpener"];
	converters     = ["GARbro[types:archive:BlackRainbow.PackOpener]"];
}
