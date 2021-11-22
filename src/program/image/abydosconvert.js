import {xu} from "xu";
import {Program} from "../../Program.js";

export class abydosconvert extends Program
{
	website       = "https://github.com/Sembiance/abydosconvert";
	gentooPackage = "media-gfx/abydosconvert";
	gentooOverlay = "dexvert";
	unsafe        = true;
	bin           = "abydosconvert"
	flags         =
	{
		format : "Which format to use for conversion. This is a mime type. REQUIRED."
	};

	args = r => ["--json", r.flags.format, r.inFile(), r.outDir()];

	// Timeout is because abydos sometimes just hangs on a conversion eating 100% CPU forever. ignore-stderr is due to wanting a clean parse of the resulting JSON
	runOptions = ({timeout : xu.MINUTE})
	renameOut = {regex : /^.+(?<pre>\.\d{3})?(?<post>\.(?:png|svg|webp))$/};
}

/*
Old Node check:
			// abydos has the nasty habit of producing 'empty' SVG files that are 0x0 when fed files that are not valid (such as image/sunRaster/OPENING.SCR which is interpreted as an image/aniST file)
			// Sadly ImageMagick identifies this as having a width/height of 300x150 for whatever stupid reason, probably some stupid built in default
			// So let's check the resulting JSON from abydos and if height & width are both zero and we only have .svg files as output, delete our output files
			const abydosResult = XU.parseJSON(r.results, {});
			if(abydosResult.width===0 && abydosResult.height===0 && !outputFilePaths.some(outputFilePath => !outputFilePath.toLowerCase().endsWith(".svg")))
				return outputFilePaths.parallelForEach((outputFilePath, subcb) => fileUtil.unlink(outputFilePath, subcb), this);
Could add this to a verify and check the stdout JSON to see and invalidate the output. So far though haven't come across this, and the OPENING.SCR doesn't yield any files now from latest abydosconvert
*/
