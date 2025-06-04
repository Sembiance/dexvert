import {Format} from "../../Format.js";

export class installShieldSelfExtractor extends Format
{
	name           = "InstallShield Self-Extractor";
	website        = "http://justsolve.archiveteam.org/wiki/InstallShield_Self-Extracting_EXE";
	ext            = [".exe"];
	forbidExtMatch = true;
	// TODO: Temporarily disabling matches to this due to wineSelfExtractor not being reliable enough. Gonna get the format reverse engineered and after I have a proper extractor I'll re-enable this
	//magic          = ["InstallShield Self-Extractor", "Win16 InstallShield Self-Extracting Executable"];
	converters     = [
		//"unshield", "unshield[oldCompression]", "isextract", "cmdTotal[wcx:InstExpl.wcx]", "UniExtract[matchType:magic][hasExtMatch]",	// I'm not aware of any SFX EXEs that these tools can actually handle, but I keep them here just in case?
		"wineSelfExtractor"
	];
}
