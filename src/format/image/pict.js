import {Format} from "../../Format.js";
import {_MACBINARY_MAGIC} from "../archive/macBinary.js";

export class pict extends Format
{
	name           = "Macintosh Picture Format";
	website        = "http://fileformats.archiveteam.org/wiki/PICT";
	ext            = [".pict", ".pic", ".pct"];
	forbidExtMatch = true;	// way too common
	mimeType       = "image/pict";
	magic          = ["QuickDraw/PICT bitmap", "Macintosh PICT", "Claris clip art", "Macintosh Pict image (MacBinary)", /^fmt\/341( |$)/, /^x-fmt\/80( |$)/];
	alwaysIdentify = true; // Always identify this format, even if explicitly called with asFormat image/pict, this way the matchType:magic flags below will properly apply
	metaProvider   = ["image"];
	converters = dexState =>
	{
		const r = ["qtPicViewer[matchType:magic]"];
		
		if(dexState.hasMagics("Macintosh Pict image (MacBinary)"))
			r.push("deark[mac][deleteADF][convertAsExt:.pict]");

		r.push(
			"deark[module:pict][mac][recombine]",
			"recoil2png"
		);

		const clarisClipArtConverters =
		[
			"soffice[matchType:magic][outType:png]"//, // soffice sometimes produces just text that says "QuickTime and a Ph..." which doesn't get detected
			//"corelPhotoPaint"		// corelPhotoPaint often just produces a 'QuickTime PICT' logo, not useful and not currently detected (see sample/image/pict/01 and sample/image/pict/747_007)
		];

		// If we have this magic, then the other converters are unlikely to produce an image, so put these first
		if(dexState.hasMagics("Claris clip art"))
			r.push(...clarisClipArtConverters);

		// even though we have forbidExtMatch above, keep the [matchType:magic] here because if dexvert is explictily called with asFormat image/pict we end up here (such as chaining from deark) and we want to avoid so many slow windows program executions
		r.push(
			"canvas[matchType:magic]",		// canvas seems to properly recombine sub-bitmaps into a final image (sample/image/pict/Daniel  and  2kangaro  and  bbq)
			"hiJaakExpress[matchType:magic]",
			"picturePublisher[matchType:magic]"
		);

		if(dexState.hasMagics(_MACBINARY_MAGIC))
			r.push("deark[module:macbinary] -> deark");	// Can handle MacBinary-encoded PICT files such as samples 35, 039 and 06
			
		r.push(
			"imageAlchemy",		// while this properly recombines sub-bitmaps, it's DOS based and so we don't trust it very much
			"graphicWorkshopProfessional[matchType:magic]",
			"corelDRAW[matchType:magic]"
		);
		
		// Otherwise this is the proper priority for those converters
		if(!dexState.hasMagics("Claris clip art"))
			r.push(...clarisClipArtConverters);

		r.push(
			"tomsViewer[matchType:magic]",		// For some PICTS will only produce the 'thumbnail' (samples 35, 039 and 06). For these files, corelPhotoPaint produces a full image so this converter is tried after that one
			"nconvert",	// nconvert produces just a black image PICT v2 format picts: p#.pic
			"convert"	// convert has a habit of just producing a black square
		);
		return r;
	};
}
