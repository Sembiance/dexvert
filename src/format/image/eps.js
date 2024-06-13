import {Format} from "../../Format.js";
import {_MACBINARY_MAGIC} from "../archive/macBinary.js";

const _EPS_MAGIC = ["Encapsulated PostScript File Format", /^PostScript document.*type EPS/, "Encapsulated PostScript binary", "DOS EPS Binary File", "Macintosh Encapsulated Postscript (MacBinary)", /^fmt\/(122|123|124|417)( |$)/, /^x-fmt\/20( |$)/];
const _EPS_EXT = [".eps", ".epsf", ".epsi", ".epi", ".ept"];
export {_EPS_MAGIC, _EPS_EXT};

export class eps extends Format
{
	name       = "Encapsulated PostScript";
	website    = "http://fileformats.archiveteam.org/wiki/Encapsulated_PostScript";
	ext        = _EPS_EXT;
	mimeType   = "application/eps";
	magic      = _EPS_MAGIC;
	idMeta     = ({macFileType}) => ["EPSF", "EPSP"].includes(macFileType);
	notes      = "We used to convert to both PNG and SVG using nconvert & inkscape. But ps2pdf[svg] works much better and supports both raster and vector versions. Still, fallback to inkscape for some files like eagle and eagle.001";
	converters = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("Macintosh Encapsulated Postscript (MacBinary)"))
			r.push("deark[mac][deleteADF][convertAsExt:.eps]");
		
		// vector
		r.push("ps2pdf[fromEPS][svg]", "inkscape");
		
		// raster
		if(!dexState.hasMagics(_MACBINARY_MAGIC))
			r.push("photoDraw");

		r.push("deark[module:eps]", "gimp", "nconvert");
		
		// only include certain long-running windows based converters if we're not dealing with a MacBinary file (archive/macBinary/1Sled Ride.EPS)
		if(!dexState.hasMagics(_MACBINARY_MAGIC))
			r.push("corelDRAW", "hiJaakExpress", "canvas[matchType:magic][nonRaster]", "picturePublisher", "keyViewPro");

		return r;
	};
}
