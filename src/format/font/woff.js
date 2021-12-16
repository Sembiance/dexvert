import {Format} from "../../Format.js";

export class woff extends Format
{
	name         = "Web Open Font Format";
	website      = "http://fileformats.archiveteam.org/wiki/WOFF";
	ext          = [".woff", ".woff2"];
	magic        = ["Web Open Font Format"];
	metaProvider = ["fc_scan"];
	converters   = ["fontforge"];
}
