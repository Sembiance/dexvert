import {Format} from "../../Format.js";

export class gusPatch extends Format
{
	name           = "Gravis Ultrasound Patch";
	website        = "http://fileformats.archiveteam.org/wiki/Gravis_Ultrasound_patch";
	ext            = [".pat", ".sbs"];
	forbidExtMatch = true;
	magic          = ["GUS patch", "Gravis UltraSound GF1 patch", "Old GUS patch", "Old GUSpatch", /^Old GUS⇥patch$/];
	converters     = ["awaveStudio"];
}
