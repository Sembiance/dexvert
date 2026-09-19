import {Format} from "../../Format.js";

export class tiareGRA extends Format
{
	name           = "Tiare GRA Image";
	ext            = [".gra"];
	forbidExtMatch = true;
	magic          = ["image:Tiare.GraFormat"];
	converters     = ["GARbro[types:image:Tiare.GraFormat]"];
}
