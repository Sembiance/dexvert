import {Format} from "../../Format.js";

export class technoBrainIPQ extends Format
{
	name           = "TechnoBrain's Animation Resource";
	ext            = [".ipf"];
	forbidExtMatch = true;
	magic          = ["archive:TechnoBrain.IpqOpener"];
	converters     = ["GARbro[types:archive:TechnoBrain.IpqOpener]"];
}
