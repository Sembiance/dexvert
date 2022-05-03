import {Format} from "../../Format.js";

export class vCard extends Format
{
	name        = "vCard";
	website     = "http://fileformats.archiveteam.org/wiki/VCard";
	ext         = [".vcf", ".vcard"];
	magic       = ["vCard - Business Card", "vCard visiting card"];
	notes       = "Could write my own parser/converter using package libvformat";
	unsupported = true;
}
