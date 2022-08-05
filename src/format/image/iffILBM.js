import {xu} from "xu";
import {Format} from "../../Format.js";

export class iffILBM extends Format
{
	name           = "IFF Interleaved Bitmap Image";
	website        = "http://fileformats.archiveteam.org/wiki/ILBM";
	ext            = [".lbm", ".ilbm", ".iff", ".beam", ".dhr", ".dr", ".mp", ".dctv"];
	mimeType       = "image/x-ilbm";
	magic          = ["IFF InterLeaved BitMap", "IFF data, ILBM interleaved image", "Interchange File Format Interleaved Bitmap", "IFF ILBM bitmap", "DCTV encoded ILBM bitmap", /^fmt\/338( |$)/];
	forbiddenMagic = ["IFF Amiga Contiguous BitMap"];	// trid likes to identify IFF ACBM files as both ACBM and ILBM, so forbid the magic here and let iffACBM handle that
	metaProvider   = ["image"];
	notes          = xu.trim`
		ILBM files are only converted to static PNG images. Color cyclying animated GIFs are not produced.
		This is because a HUGE number of ILBM files from back in the day have wacky color cycle data that yield extensive strobing or almost no change at all.
		Additionally, the animation support isn't fully working as some have REAL cycle data, but I haven't found ANY program that can handle them: V05AM.LBM V12.LBM V18.LBM V21.LBM V22.LBM V26.LBM
		Some ILBM files were only used to hold a palette and nothing more. This won't convert those.
		DPPS chunk - Present in some files and they don't convert correctly. Probably a 'Deluxe Paint' chunk of some sort`;

	// recoil2png produces the best still images for iffILBM files, with abydosconvert being a runner up
	// abydosconvert also 'stretches' the pixels to 'mimic' how they originally looked, but I don't really like that
	// abydosconvert also as of v0.2.3 doesn't handle certain images correctly such as GINA and foto57
	converters = [`recoil2png`, "deark", "ffmpeg[format:iff][outType:png]", "convert", `abydosconvert[format:${this.mimeType}][outType:png]`, "iff_convert", "hiJaakExpress[matchType:magic]", "pv[matchType:magic]", "canvas[matchType:magic]"];
}

/* Other IFF ILBM converters:
abydosconvert can produce animated WEBP files from color cycling ILBM files, but it handles several files poorly
So I wrote my own program, ilbm2frames (that uses libiff behind the scenes). ilbm2frames won't produce frames unless there is color cycling
If you use that, in combination with every converter, you can get both an animated file and a static file:
  converters = [`recoil2png`, "deark", "ffmpeg[format:iff]", "convert", `abydosconvert[format:${this.mimeType}][outType:png]`].map(v => `ilbm2frames -> *ffmpeg[fps:20][outType:gif] & ${v}`);
However, there are a TON of IFF files out there with just truly wacky color cycling, almost like some sort of odd default from some program back in the day.
So it's not really worth creating the animated versions, just way too much junk.

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
