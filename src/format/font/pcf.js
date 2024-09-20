import {Format} from "../../Format.js";

export class pcf extends Format
{
	name         = "Portable Compiled Format";
	website      = "http://fileformats.archiveteam.org/wiki/PCF";
	ext          = [".pcf", ".pmf"];
	magic        = ["X11 Portable Compiled Font data", "Portable Compiled Format font", "application/x-font-pcf", /^fmt\/1720( |$)/];
	metaProvider = ["fc_scan"];

	// If it's a .pmf file and fc_scan was able to scan it, just accept it as is, because deark doesn't work with .pmf files
	untouched  = dexState => dexState.f.input.ext.toLowerCase()===".pmf" && (dexState.meta.family || dexState.meta.subfamily || dexState.meta.fullName || dexState.meta.postScriptName);
	converters = ["deark[module:pcf]"];
}
