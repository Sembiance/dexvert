import {Format} from "../../Format.js";

export class nullsoftInstallerPackage extends Format
{
	name       = "Nullsoft Installer Package";
	website    = "http://fileformats.archiveteam.org/wiki/NSIS";
	magic      = ["Installer: Nullsoft"];
	converters = ["sevenZip[type:nsis]", "unar[type:nsis]", "cmdTotal[wcx:InstExpl.wcx]"];
}
