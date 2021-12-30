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
		Some ILBM files were only used to hold a palette and nothing more. This won't convert those.
		Others have EMPTY (zeros) CMAP palettes which confuse the converter programs. So I detect this and remove the CMAP entry which allows the converters to fallback to a default converter.
		DPPS chunk - Present in some files and they don't convert correctly. Probably a 'Deluxe Paint' chunk of some sort.
		CRNG chunk - Used for color shifting. Abydos supports some of these (used by Deluxe Paint)`;
	
	// abydosconvert is the only thing that can handle animated IFF files (color cycling, etc) (AH_Dan, AH_Eye, Watch, DECKER-BattleMech)
	// But it sometimes produces crazy fast color cycles and they can sometimes be so rapid that the original meaning of the image is lost
	// It also sometimes produces just a webp with all identical frames (which the program abydosconvert will automatically detect and delete in post())
	// abydosconvert also 'stretches' the pixels to 'mimic' how they originally looked, but I don't really like that
	// We start by running both abydosconvert and recoil2png at the same time, and recoil2png will overwrite any PNG produced by abydosconvert
	// abydosconvert also as of v0.2.3 doesn't handle certain images correctly such as GINA and foto57
	converters    = [`abydosconvert[format:${this.mimeType}] & recoil2png`, `abydosconvert[format:${this.mimeType}][outType:png]`, "deark", "ffmpeg[format:iff]", "convert"];
}

// node version of dexvert was doing this, but I didn't see any sample files that exhibit have this problem thus I couldn't test, so I'm not sure it's needed anymore
// may have been an ILBM that was used by some game that I now properly detect and handle as such
/*
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
