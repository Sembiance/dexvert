import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";
import {path} from "std";

const STANDARD_INSTRUMENTS_FILE_PATHS = await fileUtil.tree(path.join(xu.dirname(import.meta), "..", "..", "..", "music", "smusInstrument"), {nodir : true});

export class smus extends Format
{
	name    = "Simple Musical Score";
	website = "http://fileformats.archiveteam.org/wiki/Amiga_Module";
	ext     = [".smus", ".song"];
	magic   = ["SMUS IFF Simple Musical Score", "IFF data, SMUS simple music"];
	notes   = xu.trim`
		The 'SMUS' format was used by many different programs including Sonix and Deluxe Music.
		This first tries to convert SONIX SMUS with instrument support using uade123.
		That cna fail though, then falls back to SMUS2MIDI and SMUSMIDI, losing instrument samples.
		SMUS2MIDI seems to work on more files, but it gets several of them a bit wrong (Rhapsody.smus)
		SMUSMIDI is pretty good, but it crashes on many files, requiring a full timeout wait of the rexx script.`;
	
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
	converters = ["uade123", "smus2midi", "smusmidi"];
	verify // TODO needs to check the duration, which should be set from music family? see how I pass verification meta from image family
}

/*


exports.converterPriority =
[
	{program : "uade123", argsd : state => (["./in.smus", path.join(state.output.absolute, "outfile.wav")]), runOptions : state => ({cwd : state.smusWorkDir}) },
	["smus2midi", {program : "dexvert", flags : {asFormat : "music/mid", deleteInput : true}, argsd : state => ([path.join(state.output.absolute, `${state.input.name}.mid`), state.output.absolute])}],
	["smusmidi", {program : "dexvert", flags : {asFormat : "music/mid", deleteInput : true}, argsd : state => ([path.join(state.output.absolute, `${state.input.name}.mid`), state.output.absolute])}]
];

exports.postSteps = [
	(state, p) =>
	{
		const smusWorkDir = state.smusWorkDir;
		delete state.smusWorkDir;
		return p.util.file.unlink(smusWorkDir);
	}
];

*/
