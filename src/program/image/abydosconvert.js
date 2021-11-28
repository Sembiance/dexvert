import {xu} from "xu";
import {Program} from "../../Program.js";
import {runUtil} from "xutil";

export class abydosconvert extends Program
{
	website       = "https://github.com/Sembiance/abydosconvert";
	gentooPackage = "media-gfx/abydosconvert";
	gentooOverlay = "dexvert";
	unsafe        = true;
	bin           = "abydosconvert";
	flags         =
	{
		format  : "Which format to use for conversion. This is a mime type. REQUIRED.",
		outType : "Which format to output. 'png' is the only allowed option right now. Default: Let abydosconvert decide"
	};

	args = r => [...(r.flags.outType==="png" ? ["--png"] : []), "--json", r.flags.format, r.inFile(), r.outDir()];

	// abydos 0.2.9 has a bug where on FIRST run, it writes a file to HOME/.cache/abydos/plugins.cache
	// It then proceeds to convert the file. HOWEVER on some image formats (avatar cebraText mrgSystemsText softelText teletextPackets) this first run will produce red artifacts on the image randomly
	// Doing a --list first will 'prime' the HOME dir that was set up
	pre = async r => await runUtil.run("abydosconvert", ["--list"], {env : {HOME : r.f.homeDir.absolute}});

	// Timeout is because abydos sometimes just hangs on a conversion eating 100% CPU forever. ignore-stderr is due to wanting a clean parse of the resulting JSON
	runOptions = ({timeout : xu.MINUTE});
	renameOut =
	{
		regex : /.+?(?<num>\.\d{3})?(?<ext>\.(?:png|svg|webp))$/,
		renamer :
		[
			({suffix, newName}, {ext}) => [newName, suffix, ext],
			({suffix}, {num, ext}) => [num.trimChars("."), suffix, ext]
			//({fn, suffix}, {num, name, ext}) => { console.log({fn, num, name, ext}); return false; }
		]
	};
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
