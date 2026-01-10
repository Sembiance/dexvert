import {Format} from "../../Format.js";
import {_MACBINARY_MAGIC} from "../archive/macBinary.js";

export class gif extends Format
{
	name         = "Graphics Interchange Format";
	website      = "http://fileformats.archiveteam.org/wiki/GIF";
	ext          = [".gif"];
	mimeType     = "image/gif";
	magic        = [
		// generic GIF
		"GIF image data", "GIF animated bitmap", "image/gif", "CompuServe Graphics Interchange Format (GIF) (gif)", "deark: gif", /^GIF8[79]a bitmap$/, /^GIF8[79]-Bild/, "Compuserve GIF", /^fmt\/(3|4)( |$)/,	//eslint-disable-line sonarjs/single-character-alternation
		"GIF (with Length Prefix)",

		// app specific
		"Mac PageMill's GIF bitmap (MacBinary)", "Fractint saved bitmap", "Fractint Continuous Potential Image"
	];
	idMeta           = ({macFileType}) => ["GIFf", "GIFF", "GIF ", "gif "].includes(macFileType);
	untouched        = r => r.meta.width && r.meta.height;		// if we were able to get our image meta info, then we are a valid GIF and should leave it alone
	metaProvider     = ["image", "gifsicle_info"];
	confidenceAdjust = (inputFile, matchType, curConfidence, {detections}) => (detections.some(o => o.value.startsWith("fmt/1708")) ? -1 : 0);	// document/aldusPersuasionPlayerFile

	// some GIF files are often corrupted and Imagemagick won't load them (butts09.gif), thus no meta data. However nconvert can usually handle them, so we try converting to PNG if no meta data found
	// deark handles some very old animated GIFs that are slightly broken such as 89aillus.gif by simply extracting out the individual frames
	converters = dexState =>
	{
		const r = [];
		if(dexState.hasMagics(["Mac PageMill's GIF bitmap (MacBinary)", ..._MACBINARY_MAGIC]))
			r.push("deark[module:macbinary][mac][deleteADF][convertAsExt:.gif]", "deark[module:macbinary]");
		r.push("iconvert", "nconvert[format:gif]", "deark[module:gif]");
		
		r.push(...["foremost", "keyViewPro", "photoDraw", "hiJaakExpress", "picturePublisher", "corelPhotoPaint", "canvas5[strongMatch]", "canvas[strongMatch]", "tomsViewer", "corelDRAW"].map(v => `${v}[matchType:magic])`));
		return r;
	};
}
