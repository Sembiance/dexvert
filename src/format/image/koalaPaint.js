import {Format} from "../../Format.js";

export class koalaPaint extends Format
{
	name       = "Koala Paint";
	website    = "http://fileformats.archiveteam.org/wiki/KoalaPainter";
	ext        = [".koa", ".gig", ".kla", ".gg", ".koala"];
	safeExt  = dexState =>
	{
		if([10003, 10006].includes(dexState.f.input.size))
			return ".koa";

		// nconvert requires a proper file extension. If the file is not 10,003 or 10,006 bytes, we assume it is compressed and needs a .gg extension to convert correctly
		return ".gg";
	};
	mimeType   = "image/x-koa";
	magic      = ["Koala Paint"];
	trustMagic = true;	// Koala Paint is normally untrustworthy, but we trust it here
	converters = ["nconvert", `abydosconvert[format:${this.mimeType}]`, "view64"]

	// Must be greater <= 10006 because either we are uncompressed (10003/10006) or we are compresed in which case we should be smaller
	idCheck = inputFile => inputFile.size<=10006;
}
