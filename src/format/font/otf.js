import {Format} from "../../Format.js";

export class otf extends Format
{
	name         = "OpenType Font";
	website      = "http://fileformats.archiveteam.org/wiki/OpenType";
	ext          = [".otf"];
	magic        = [/^OpenType [Ff]ont/];
	metaProvider = ["fc_scan"];
	converters   = dexState => [`fontPreview[family:${dexState.meta.family}]`];
}
