import {fileUtil} from "xutil";
import {Format} from "../../Format.js";

const _MAGIC = [0x13, 0x5D, 0x65, 0x8C, 0x3A, 0x01, 0x02, 0x00];

export class installShieldSelfExtractor extends Format
{
	name           = "InstallShield Self-Extractor";
	website        = "http://justsolve.archiveteam.org/wiki/InstallShield_Self-Extracting_EXE";
	ext            = [".exe"];
	forbidExtMatch = true;
	priority       = this.PRIORITY.HIGH;
	magic          = ["InstallShield Self-Extractor", "Win16 InstallShield Self-Extracting Executable"];
	idCheck        = async inputFile => inputFile.size>_MAGIC.length && (await fileUtil.readFileBytes(inputFile.absolute, _MAGIC)).indexOfX(_MAGIC)!==0;
	forbiddenMagic = ["Win32 Dynamic Link Library"];
	converters     = ["unISV3", "installShieldSelfExtractor", "deark[module:exe][opt:exe:sfx]"];
	verify         = ({newFile}) => !["_setup.lib", "_setup32.lib"].includes(newFile.base.toLowerCase());	// these files are already extracted by the installer, so no need to keep them around to just be extracted again by a dexrecurse
}
