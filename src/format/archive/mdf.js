import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class mdf extends Format
{
	name           = "Alcohol 120% MDF Image";
	website        = "http://fileformats.archiveteam.org/wiki/MDF_and_MDS";
	ext            = [".mdf"];
	magic          = ["ISO 9660 CD image", "Raw CD image"];
	weakMagic      = true;
	forbiddenMagic = TEXT_MAGIC;
	priority       = this.PRIORITY.TOP;
	// First try uniso, that correctly handles things like: Earthcare Interactve
	// Second try processing AS an ISO, this correctly handles: DOKAN23
	// Third, iat can often just produce a .cue and no bin. This happens if the file is actually just an ISO or raw parititon
	converters = ["uniso", "dexvert[asFormat:archive/iso][forbidProgram:IsoBuster]", "iat", "MDFtoISO"];
}
