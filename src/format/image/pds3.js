import {Format} from "../../Format.js";

export class pds3 extends Format
{
	name           = "Planetary Data System v3";
	website        = "http://fileformats.archiveteam.org/wiki/PDS";
	ext            = [".img", ".imq", ".pds"];
	forbidExtMatch = [".img"];
	magic          = ["Detached PDS Label info (v3)", /^PDS image data/];
	converters     = ["pdsTransformTool"];
}
