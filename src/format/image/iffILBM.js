import {xu} from "xu";
import {Format} from "../../Format.js";

export class iffILBM extends Format
{
	name     = "IFF Interleaved Bitmap Image";
	website  = "http://fileformats.archiveteam.org/wiki/ILBM";
	ext      = [".lbm", ".ilbm", ".iff", ".beam", ".dhr", ".dr", ".mp", ".dctv"];
	mimeType = "image/x-ilbm";
	magic    = ["IFF InterLeaved BitMap", "IFF data, ILBM interleaved image", "Interchange File Format Interleaved Bitmap", "IFF ILBM bitmap", "DCTV encoded ILBM bitmap"];
	notes    = xu.trim`
		Some ILBM files were only used to hold a palette and nothing more. This won't convert those.
		Others have EMPTY (zeros) CMAP palettes which confuse the converter programs. So I detect this and remove the CMAP entry which allows the converters to fallback to a default converter.
		DPPS chunk - Present in some files and they don't convert correctly. Probably a 'Deluxe Paint' chunk of some sort.
		CRNG chunk - Used for color shifting. Abydos supports some of these (used by Deluxe Paint)`;
	
	// abydosconvert handles IFF files the best (BY FAR), including color cycling animations in WEBP format (AH_Dan, AH_Eye, Watch, DECKER-BattleMech)
	// But it sometimes produces crazy fast color cycles and they can sometimes be so rapid that the original meaning of the image is lost
	// It also as of v0.2.3 doesn't handle certain images correctly such as GINA and foto57
	// So we first run both abydosconvert and recoil2png. abydos will produce a .webp for it's animated output which the other programs don't produce
	converters = [`abydosconvert[format:${this.mimeType}] & recoil2png`, "deark", "ffmpeg[format:iff]", "convert"];
}

// node version of dexvert was doing this, but I didn't see any sample files that exhibit have this problem thus I couldn't test, so I'm not sure it's needed anymore
// may have been an ILBM that was used by some game that I now properly detect and handle as such
/*
exports.preSteps =
[
	function loadFileData()
	{
		fs.readFile(state.input.absolute, this);
	},
	function checkForNullCMAPPalette(inputBuffer)
	{
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
	);
]
*/
