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
	converters     = dexState =>
	{
		const r = ["uniso"];	// Try uniso first, so files like 'Earthcare Interactive' are handled correctly
		
		if(dexState.hasMagics("Raw CD image, Mode 2"))	// mode 2 detected files (bluelight.mdf) are best sent directly to dexvert as an ISO
			r.push("dexvert[asFormat:archive/iso][forbidProgram:IsoBuster]", "iat");
		else
			r.push("iat", "dexvert[asFormat:archive/iso][forbidProgram:IsoBuster]");	// otherwise try iat first but then try as an ISO to handle DOKAN23
		r.push("MDFtoISO");

		return r;
	};
}
