import {Format} from "../../Format.js";

export class okt extends Format
{
	name         = "Oktalyzer Module";
	website      = "http://fileformats.archiveteam.org/wiki/Oktalyzer_module";
	ext          = [".okt", ".okta", ".ok"];
	magic        = ["Oktalyzer module", "Oktalyzer Audio file", /^fmt\/722( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123", "uade123"];
}
