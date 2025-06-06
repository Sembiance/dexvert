import {Format} from "../../Format.js";

export class installShieldSelfExtractor extends Format
{
	name           = "InstallShield Self-Extractor";
	website        = "http://justsolve.archiveteam.org/wiki/InstallShield_Self-Extracting_EXE";
	ext            = [".exe"];
	forbidExtMatch = true;
	priority       = this.PRIORITY.HIGH;
	magic          = ["InstallShield Self-Extractor", "Win16 InstallShield Self-Extracting Executable"];
	converters     = ["installShieldSelfExtractor"];
	verify         = ({newFile}) => !["_setup.lib", "_setup32.lib"].includes(newFile.base.toLowerCase());	// these files are already extracted by the installer, so no need to keep them around to just be extracted again by a dexrecurse
}
