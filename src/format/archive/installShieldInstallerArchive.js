import {Format} from "../../Format.js";

export class installShieldInstallerArchive extends Format
{
	name        = "InstallShield Installer Archive";
	website     = "http://fileformats.archiveteam.org/wiki/InstallShield_installer_archive";
	ext         = [".ex_"];
	magic       = ["Stirling Technologies InstallShield compressed"];
	unsupported = true;
}

