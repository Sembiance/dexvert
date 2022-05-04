import {Format} from "../../Format.js";

export class gemMetafile extends Format
{
	name       = "GEM Vector Metafile";
	website    = "http://fileformats.archiveteam.org/wiki/GEM_VDI_Metafile";
	ext        = [".gem", ".gdi"];
	magic      = [/^GEM [Mm]etafile/, /^fmt\/542( |$)/];
	notes      = "Vector file format that could be converted into SVG. abydos is working on adding support for this format.";
	converters = ["corelPhotoPaint"];
}
