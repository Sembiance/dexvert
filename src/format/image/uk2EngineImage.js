import {Format} from "../../Format.js";

export class uk2EngineImage extends Format
{
	name           = "UK2 Engine Image";
	ext            = [".pdt", ".anm"];
	forbidExtMatch = true;
	magic          = ["image:AyPio.Pdt5Format"];
	weakMagic      = true;
	converters     = ["GARbro[types:image:AyPio.Pdt5Format]"];
}
