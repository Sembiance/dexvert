import {Format} from "../../Format.js";

export class dynamicStudio extends Format
{
	name        = "Dynamic Studio Professional Module";
	website     = "http://fileformats.archiveteam.org/wiki/Dynamic_Studio_Professional_module";
	ext         = [".dsm", ".dsp"];
	magic       = ["Dynamic Studio Professional module"];
	converters  = ["zxtune123", "vgmstream", "openmpt123"];
}
