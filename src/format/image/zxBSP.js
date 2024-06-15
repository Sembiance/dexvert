import {Format} from "../../Format.js";

export class zxBSP extends Format
{
	name           = "ZX Spectrum BSP";
	website        = "http://fileformats.archiveteam.org/wiki/BSP_(ZX_Spectrum)";
	ext            = [".bsp"];
	forbidExtMatch = true;
	magic          = ["ZX Spectrum BSP", "BSP bitmap"];
	weakMagic      = ["BSP bitmap"];
	converters     = ["recoil2png[strongMatch]"];
}
