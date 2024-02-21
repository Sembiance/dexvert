import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

const INSTRUMENT_NAMES = ["eaw", "fluid", "roland", "creative", "freepats", "windows"];	// Ordered by best sounding
const INSTRUMENT_DIR_PATH = path.resolve(path.join(import.meta.dirname, "..", "..", "..", "music", "midiFont"));

export class timidity extends Program
{
	website = "http://timidity.sourceforge.net/";
	package = ["media-sound/timidity++", "media-sound/timidity-freepats", "media-sound/fluid-soundfont", "media-sound/timidity-eawpatches"];
	unsafe  = true;
	flags   = {
		midiFont : `Which midifont to use to convert (${INSTRUMENT_NAMES.join(", ")}) Default: ${INSTRUMENT_NAMES[0]}`
	};

	bin = "timidity";

	// Some MIDI files are buggy and have 2 hour+ run times, others seem to loop for hours. So specify a sane timeout, it'll then handle the WAV that it did produce, which will be good enough
	runOptions = ({timeout : xu.MINUTE*2});

	args = async r =>
	{
		const midiFont = r.flags.midiFont || INSTRUMENT_NAMES[0];

		r.instrumentDirPath = INSTRUMENT_NAMES.includes(midiFont) ? path.join(INSTRUMENT_DIR_PATH, midiFont) : await fileUtil.genTempPath(r.f.root, "_timidity_instrument");
		
		// If we didn't have that instrument name, assume we've been passed a file path to a specific sound font to use instead
		if(!INSTRUMENT_NAMES.includes(midiFont))
		{
			await Deno.mkdir(r.instrumentDirPath, {recursive : true});
			await Deno.symlink(midiFont, path.join(r.instrumentDirPath, path.basename(midiFont)));
			await fileUtil.writeTextFile(path.join(r.instrumentDirPath, "timidity.cfg"), `dir ${r.instrumentDirPath}\nsoundfont "${path.basename(midiFont)}" order=0`);
		}
		
		return ["-c", path.join(r.instrumentDirPath, "timidity.cfg"), "-Ow", "-o", await r.outFile("out.wav"), r.inFile()];
	};

	renameOut = true;
	chain     = `sox[maxDuration:${xu.MINUTE*10}]`;
}
