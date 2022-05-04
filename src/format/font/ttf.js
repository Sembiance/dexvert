import {Format} from "../../Format.js";

export class ttf extends Format
{
	name         = "TrueType Font";
	website      = "http://fileformats.archiveteam.org/wiki/TTF";
	ext          = [".ttf"];
	magic        = ["TrueType Font", "TrueType Font data", /^x-fmt\/453( |$)/];
	metaProvider = ["fc_scan"];
	converters   = dexState => [`fontPreview[family:${dexState.meta.family}]`];
}
