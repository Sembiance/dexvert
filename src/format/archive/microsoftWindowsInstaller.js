import {Format} from "../../Format.js";

export class microsoftWindowsInstaller extends Format
{
	name           = "Microsoft Windows Installer";
	website        = "http://fileformats.archiveteam.org/wiki/Windows_Installer";
	ext            = [".msi", ".msp"];
	magic          = ["Microsoft Windows Installer", "Installer: Microsoft Installer", "Installer: Microsoft Compound-based installer (MSI)"];
	forbiddenMagic = ["Camtasia Studio Screen Recording", "Revit Family Architecture project", /^fmt\/(1349|1852)( |$)/];
	converters     = ["sevenZip", "cabextract"];
}
