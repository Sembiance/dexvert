import {Format} from "../../Format.js";

export class asciiFontMetrics extends Format
{
	name           = "ASCII Font Metrics";
	ext            = [".afm"];
	forbidExtMatch = true;
	magic          = ["ASCII font metrics", "Outline Font Metric", "Adobe/Outline Font Metric", "ASCII Font Metrics"];
	forbiddenMagic = [/\(MacBinary\)$/];
	priority       = this.PRIORITY.LOW;
	untouched      = true;
	metaProvider   = ["text"];
}
