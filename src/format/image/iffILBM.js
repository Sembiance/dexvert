import {xu} from "xu";
import {Format} from "../../Format.js";

export class iffILBM extends Format
{
	name           = "IFF Interleaved Bitmap Image";
	website        = "http://fileformats.archiveteam.org/wiki/ILBM";
	ext            = [".lbm", ".ilbm", ".iff", ".beam", ".dhr", ".dr", ".mp", ".dctv"];
	mimeType       = "image/x-ilbm";
	magic          = ["IFF InterLeaved BitMap", "IFF data, ILBM interleaved image", "Interchange File Format Interleaved Bitmap", "IFF ILBM bitmap", "DCTV encoded ILBM bitmap"];
	forbiddenMagic = ["IFF Amiga Contiguous BitMap"];	// trid likes to identify IFF ACBM files as both ACBM and ILBM, so forbid the magic here and let iffACBM handle that
	metaProvider   = ["image"];
	notes          = xu.trim`
		Several ILBM files from back in the day have truly wacky color cycling values that cause for extensive strobing or almost no change at all. I try and filter these out.
		Other ILBM files have color cycling set, but no program is able to handle them (V05AM.LBM V12.LBM V18.LBM V21.LBM V22.LBM V26.LBM), so those just get static images.
		Some ILBM files were only used to hold a palette and nothing more. This won't convert those.
		DPPS chunk - Present in some files and they don't convert correctly. Probably a 'Deluxe Paint' chunk of some sort`;

	// recoil2png produces the best still images for iffILBM files, with abydosconvert being a runner up
	// abydosconvert can also produce animated WEBP files from color cycling ILBM files, but it handles several files poorly
	// abydosconvert also 'stretches' the pixels to 'mimic' how they originally looked, but I don't really like that
	// so instead we run my ilbm2frames program in combination with every converter, to produce both an animated file and a static file
	// ilbm2frames won't produce frames unless there is color cycling
	// abydosconvert also as of v0.2.3 doesn't handle certain images correctly such as GINA and foto57
	converters = [`recoil2png`, `abydosconvert[format:${this.mimeType}][outType:png]`, "deark", "ffmpeg[format:iff]", "convert"].map(v => `ilbm2frames -> *ffmpeg[fps:20][outType:gif] & ${v}`);
}

/* Other IFF ILBM converters:

Tried:
	http://www.randelshofer.ch/multishow/		Does a good job at showing color cycling
	https://github.com/scemino/ColorCycling		All images loaded are all corrupt
	https://github.com/svanderburg/amiilbm		Amiga Only, but my ilbm2frames is based on code this uses
	https://github.com/Gargaj/ILBMViewer		Windows Only, can't open much
	https://github.com/wjaguar/mtPaint			Opens IFF images, but couldn't find way to see cycling
	http://grafx2.chez.com						Opens IFF images, but couldn't find way to see cycling
	https://github.com/jhuckaby/lbmtool			Converts files to JSON data

Not tried:
	http://www.effectgames.com/effect/article-Old_School_Color_Cycling_with_HTML5.html

	http://www.randelshofer.ch/monte/
	http://www.randelshofer.ch/monte/javadoc/org/monte/media/anim/ANIMDecoder.html
*/


// node version of dexvert was doing this, but I didn't see any sample files that exhibit have this problem thus I couldn't test, so I'm not sure it's needed anymore
// may have been an ILBM that was used by some game that I now properly detect and handle as such
/*
// notes : Others have EMPTY (zeros) CMAP palettes which confuse the converter programs. So I detect this and remove the CMAP entry which allows the converters to fallback to a default converter.
exports.preSteps =
	const inputBuffer = fs.readFileSync(state.input.absolute, this);

	// Some IFF files have a CMAP entries, but it's filled with all zeroes. Here we DELETE the CMAP entry if that's the case, so that the converter programs fall back on a 'default' palette of colors
	const cmapLoc = inputBuffer.indexOf("CMAP");
	if(cmapLoc===-1)
		return this();
	
	const cmapSize = inputBuffer.readUInt32BE(cmapLoc+4);
	if(Buffer.compare(inputBuffer.slice(cmapLoc+8, cmapLoc+8+cmapSize), Buffer.alloc(cmapSize, 0))===0)
	{
		state.input.filePath = fileUtil.generateTempFilePath("", ".ilbm");
		return fs.writeFile(state.input.filePath, Buffer.concat([inputBuffer.slice(0, cmapLoc), inputBuffer.slice(cmapLoc+8+cmapSize)]), this);
	}
*/
