import {Format} from "../../Format.js";

export class mdf extends Format
{
	name       = "Alcohol 120% MDF Image";
	website    = "http://fileformats.archiveteam.org/wiki/MDF_and_MDS";
	ext        = [".mdf"];
	magic      = ["ISO 9660 CD image"];
	weakMagic  = true;
	priority   = this.PRIORITY.TOP;
	converters = ["dexvert[asFormat:archive/iso]", "iat", "MDFtoISO", "IsoBuster"];	// Sometimes it's just an ISO file that uniso can handle, so try that first, otherwise 'iat' only produces a single .cue file and no bin
}
