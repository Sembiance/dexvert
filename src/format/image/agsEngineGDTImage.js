import {Format} from "../../Format.js";

export class agsEngineGDTImage extends Format
{
	name           = "AGS Engine GDT Image";
	ext            = [".gdt", ".da1"];
	forbidExtMatch = true;
	magic          = ["image:CsWare.GdtFormat"];
	converters     = ["GARbro[types:image:CsWare.GdtFormat]"];
}
