import {Format} from "../../Format.js";

export class navyDIF extends Format
{
	name        = "NAVY DIF";
	website     = "https://www.govinfo.gov/content/pkg/GOVPUB-C13-54457a38751dd2826804944b2be585f3/pdf/GOVPUB-C13-54457a38751dd2826804944b2be585f3.pdf";
	ext         = [".dif"];
	unsupported = true;
	converters  = ["softwareBridge[format:navyDIF]", "wordForWord"];
	notes       = "A format from the US NAVY for interchanging word processing files. Haven't investigated it for magic.";
}
