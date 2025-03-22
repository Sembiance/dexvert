import {Format} from "../../Format.js";

export class nsf extends Format
{
	name           = "NES Sound File";
	website        = "http://fileformats.archiveteam.org/wiki/NES_Sound_Format";
	ext            = [".nsf", ".nsfe"];
	forbidExtMatch = true;
	magic          = ["NES Sound File", "NES Sound Format rip", "Extended Nintendo Sound Format chiptune", "Extended NES Sound File"];
	metaProvider   = ["musicInfo"];
	converters     = ["zxtune123[largeQuota][trimSilence]"];
}
