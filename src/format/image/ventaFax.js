import {Format} from "../../Format.js";

export class ventaFax extends Format
{
	name           = "Venta Fax";
	ext            = [".vfx"];
	forbidExtMatch = true;
	magic          = ["Venta Fax :vfx:"];
	converters     = ["nconvert[format:vfx]"];
}
