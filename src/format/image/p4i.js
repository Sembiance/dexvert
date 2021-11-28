import {Format} from "../../Format.js";

export class p4i extends Format
{
	name       = "P4I";
	website    = "http://fileformats.archiveteam.org/wiki/P4I";
	ext        = [".p4i"];
	magic      = ["Picasso 64 Image", "Saracen Paint Image", "Koala Paint"];
	weakMagic  = true;
	trustMagic = true;	// Koala Paint is normally untrustworthy, but we trust it here
	converters = ["recoil2png"];
}
