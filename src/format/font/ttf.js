import {Format} from "../../Format.js";
import {imageUtil} from "xutil";

export class ttf extends Format
{
	name    = "TrueType Font";
	website = "http://fileformats.archiveteam.org/wiki/TrueType";
	ext     = [".ttf"];
	magic   = [
		"TrueType Font", "TrueType Font data", "Truetype Schriftart", "Format: TrueType font", "font/ttf", /^x-fmt\/453( |$)/,

		"TrueType/OpenType Font Collection"	// this is actually a 'collection' of ttf fonts, but it's more modern and the samples I found I couldn't properly extract the fonts with the tool I tried. seems to process fine as a single font for now
	];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="sfnt" && macFileCreator==="movr";
	metaProvider = ["fc_scan"];
	converters   = ["convert[format:TTF][background:#C0C0C0][matchType:magic]"];
	verify       = async ({newFile}) => (await imageUtil.getInfo(newFile.absolute))?.colorCount>1;
}
