import {Format} from "../../Format.js";

export class os2InstallPackage extends Format
{
	name       = "OS/2 Installation Package";
	website    = "http://fileformats.archiveteam.org/wiki/OS/2_PACK_archive";
	ext        = [".pkg", ".pak"];
	magic      = ["OS/2 installation package/archive", "OS/2 PACK Variant", "IBM Pack Archiv gefunden"];
	converters = ["deark[module:os2pack2]", "deark[module:os2pack]"];
}
