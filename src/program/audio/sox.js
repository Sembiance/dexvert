import {Program} from "../../Program.js";

export class sox extends Program
{
	website     = "http://sox.sourceforge.net";
	package     = "media-sound/sox";
	bin         = "sox";
	flags       = {
		bits       : "Input bits per sample",
		channels   : "Input channel count",
		encoding   : "Input encoding",
		endianness : "Input endianness. Valid: little || big.",
		rate       : "Input sampling rate",
		type       : "Input file type. Run `man soxformat` for a list"
	};

	args = async r =>
	{
		const a = [];
		if(r.flags.type)
			a.push("-t", r.flags.type);
		if(r.flags.rate)
			a.push("-r", r.flags.rate);
		if(r.flags.encoding)
			a.push("-e", r.flags.encoding);
		if(r.flags.endianness)
			a.push("--endian", r.flags.endianness);
		if(r.flags.bits)
			a.push("-b", r.flags.bits);
		if(r.flags.channels)
			a.push("-c", r.flags.channels);

		a.push(r.inFile(), await r.outFile("out.wav"));
		return a;
	};

	// We often send WAV files through SOX just to clean them up before going to FFMPEG. This sometimes results in an identical output file which is normally detected and deleted, but in this case we want to allow it
	allowDupOut = true;
	
	chain = "ffmpeg[outType:mp3]";
}
