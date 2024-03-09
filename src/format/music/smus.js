import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";
import {path} from "std";

const STANDARD_INSTRUMENTS_FILE_PATHS = await fileUtil.tree(path.join(import.meta.dirname, "..", "..", "..", "music", "smusInstrument"), {nodir : true});

export class smus extends Format
{
	name    = "Simple Musical Score";
	website = "http://fileformats.archiveteam.org/wiki/SMUS";
	ext     = [".smus", ".song"];
	magic   = ["SMUS IFF Simple Musical Score", "IFF data, SMUS simple music"];
	notes   = xu.trim`
		The 'SMUS' format was used by many different programs including Sonix and Deluxe Music.
		This first tries to convert SONIX SMUS with instrument support using uade123.
		That can fail though, then falls back to SMUS2MIDI and SMUSMIDI, losing instrument samples.
		SMUS2MIDI seems to work on more files, but it gets several of them a bit wrong (Rhapsody.smus)`;
	
	pre = async dexState =>
	{
		const songInstrumentFilePaths = await fileUtil.tree(path.join(dexState.original.input.dir, "..", "Instruments"), {nodir : true});
		const cwdInstrumentsDirPath = path.join(dexState.f.root, "Instruments");
		await Deno.mkdir(cwdInstrumentsDirPath, {recursive : true});
		await [...STANDARD_INSTRUMENTS_FILE_PATHS, ...songInstrumentFilePaths].parallelMap(async instrumentSrcFilePath =>
		{
			const instrumentDestFilePath = path.join(cwdInstrumentsDirPath, path.basename(instrumentSrcFilePath));
			if(await fileUtil.exists(instrumentDestFilePath))
				return;

			await Deno.symlink(instrumentSrcFilePath, instrumentDestFilePath);
		}, 1);
	};
	converters = ["uade123", "smus2midi"];	// The last entry used to be smusmidi back when we supported amiga under QEMU

	// Ensure the result is at least 1 second long, otherwise it likely didn't work and it should move to the next converter
	verify = ({meta}) => meta.duration>=xu.SECOND;
}
