import {Format} from "../../Format.js";

export class yaneuraoImage extends Format
{
	name           = "Yaneurao Image";
	ext            = [".yga"];
	forbidExtMatch = true;
	magic          = ["image:Yaneurao.YgaFormat"];
	converters     = ["GARbro[types:image:Yaneurao.YgaFormat]"];
}
