import {xu} from "xu";
import {Program} from "../../Program.js";
import {runUtil} from "xutil";

export class abydosconvert extends Program
{
	website  = "https://github.com/Sembiance/abydosconvert";
	package  = "media-gfx/abydosconvert";
	unsafe   = true;
	bin      = "abydosconvert";
	classify = true;
	flags    = {
		format  : "Which format to use for conversion. This is a mime type. REQUIRED.",
		outType : "Which format to output. 'png' and 'webp' are the allowed options. Default: Let abydosconvert decide"
	};

	args = r => [...(r.flags.outType==="png" ? ["--png"] : []), "--json", r.flags.format, r.inFile(), r.outDir()];

	// abydos 0.2.9 has a bug where on FIRST run, it writes a file to HOME/.cache/abydos/plugins.cache
	// It then proceeds to convert the file. HOWEVER on some image formats (avatar cebraText mrgSystemsText softelText teletextPackets) this first run will produce red artifacts on the image randomly
	// Doing a --list first will 'prime' the HOME dir that was set up
	pre = async r => await runUtil.run("abydosconvert", ["--list"], {env : {HOME : r.f.homeDir.absolute}});

	// webp files abydos produces have all identical frames, in these cases better to just delete the webp file and have it re-run and convert to PNG or let some other converter handle the PNG creation
	verify = async (r, dexFile) =>
	{
		// abydosconvert will always put a .webp extension on it
		if(dexFile.ext.toLowerCase()!==".webp")
			return true;
		
		const {meta : webpInfo} = await Program.runProgram("webpmuxInfo", dexFile, {xlog : r.xlog, autoUnlink : true});
		if(!webpInfo?.numberOfFrames || (webpInfo?.frameSizesUnique || []).length<=1)
			return false;

		return true;
	};

	// Timeout is because abydos sometimes just hangs on a conversion eating 100% CPU forever. ignore-stderr is due to wanting a clean parse of the resulting JSON
	// We run webp output a little longer since those animations can take some time to finish rendering
	runOptions = r => ({timeout : (r.flags.outType==="webp" ? xu.MINUTE*3 : xu.MINUTE)});
	renameOut = {
		regex : /.+?(?<num>\.\d{3})?(?<ext>\.(?:png|svg|webp))$/,
		renamer :
		[
			({suffix, newName}, {ext}) => [newName, suffix, ext],
			({suffix}, {num, ext}) => [num.trimChars("."), suffix, ext]
		]
	};
}
