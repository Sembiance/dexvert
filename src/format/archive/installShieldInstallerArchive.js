import {Format} from "../../Format.js";

export class installShieldInstallerArchive extends Format
{
	name       = "InstallShield Installer Archive";
	website    = "http://fileformats.archiveteam.org/wiki/InstallShield_installer_archive";
	ext        = [".ex_"];
	magic      = ["Stirling Technologies InstallShield compressed", "INS Archiv gefunden", "Archive: InstallShield INST", "deark: is_instarch", /^fmt\/1466( |$)/];
	converters = ["deark[module:is_instarch]"];
}
