import {Format} from "../../Format.js";

export class squeeze extends Format
{
	name       = "Squeeze Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Squeeze";
	magic      = [/Squeezed .*data/, "squeezed data", "Squeeze compressed archive"];
	// We don't set packed = true here because we don't have a standard extension
	converters = ["unar", "lbrate", "deark[module:squeeze]"];
}
