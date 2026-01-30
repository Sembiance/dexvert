import {Format} from "../../Format.js";

export class amiBIOSLogoSplashBitmap extends Format
{
	name           = "AMI BIOS logo/splash bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/GRFX";
	ext            = [".grfx", ".grf"];
	forbidExtMatch = true;
	magic          = ["AMI BIOS logo/splash bitmap"];
	converters     = ["wuimg[format:amibios]"];
}
