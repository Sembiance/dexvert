import {Format} from "../../Format.js";

export class realLivePDT extends Format
{
	name           = "RealLive PDT10 image";
	ext            = [".pdt"];
	forbidExtMatch = true;
	magic          = ["RealLive PDT10 image", "image:RealLive.PdtFormat"];
	converters     = ["wuimg[format:pdt]", "GARbro[types:image:RealLive.PdtFormat]"];
}
