import {Format} from "../../Format.js";

export class microsoftWindowsInstaller extends Format
{
	name       = "Microsoft Windows Installer";
	ext        = [".msi", ".msp"];
	magic      = ["Microsoft Windows Installer"];
	converters = ["sevenZip", "cabextract"];
}
