import {Format} from "../../Format.js";

export class microsoftWindowsInstaller extends Format
{
	name       = "Microsoft Windows Installer";
	website    = "http://fileformats.archiveteam.org/wiki/Windows_Installer";
	ext        = [".msi", ".msp"];
	magic      = ["Microsoft Windows Installer"];
	converters = ["sevenZip", "cabextract"];
}
