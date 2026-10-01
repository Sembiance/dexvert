import {Format} from "../../Format.js";

export class fmodSampleBank extends Format
{
	name           = "FMOD Sample Bank";
	website        = "http://fileformats.archiveteam.org/wiki/FMOD_Sample_Bank";
	ext            = [".fsb", ".bank"];
	forbidExtMatch = true;
	magic          = ["FMOD Sample Bank format", "FMOD Sample Bank", /^geArchive: FSB_FSB[54321]( |$)/, "audio:Fmod.Fsb5Audio"];
	converters     = ["vgmstream[extractAll]", "gameextractor[codes:FSB_FSB5,FSB_FSB4,FSB_FSB3,FSB_FSB2,FSB_FSB1]", "zxtune123"];
}
