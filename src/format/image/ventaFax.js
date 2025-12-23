import {Format} from "../../Format.js";

export class ventaFax extends Format
{
	name           = "Venta Fax";
	website        = "http://fileformats.archiveteam.org/wiki/VentaFax";
	ext            = [".vfx"];
	forbidExtMatch = true;
	magic          = ["VentaFax graphics", "Venta Fax :vfx:"];
	converters     = ["nconvert[format:vfx]"];
}
