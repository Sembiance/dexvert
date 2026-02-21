import {Format} from "../../Format.js";

export class nullsoftInstallerPackage extends Format
{
	name       = "Nullsoft Installer Package";
	website    = "http://fileformats.archiveteam.org/wiki/NSIS";
	magic      = ["Installer: Nullsoft", "NSIS - Nullsoft Scriptable Install System", "overlay: other/nullsoftInstallData"];
	converters = ["sevenZip[type:nsis]", "unar[type:nsis]", "cmdTotal[wcx:InstExpl.wcx]"];
}
