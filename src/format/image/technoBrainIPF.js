import {Format} from "../../Format.js";

export class technoBrainIPF extends Format
{
	name           = "TechnoBrain's Inteligent Picture Format";
	ext            = [".ipf"];
	forbidExtMatch = true;
	magic          = ["image:TechnoBrain.IpfFormat"];
	converters     = ["GARbro[types:image:TechnoBrain.IpfFormat]"];
}
