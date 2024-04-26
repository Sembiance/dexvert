import {Format} from "../../Format.js";

export class os2InstallPackage extends Format
{
	name       = "OS/2 Installation Package";
	ext        = [".pkg", ".pak"];
	magic      = ["OS/2 installation package/archive"];
	converters = ["deark[module:os2pack2]", "deark[module:os2pack]"];
	notes      = "Could support this with OS/2 unpack if I ever emulated OS/2";
}
