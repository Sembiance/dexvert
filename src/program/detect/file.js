import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class file extends Program
{
	website = "https://www.darwinsys.com/file/";
	package = "sys-apps/file";
	bin     = "file";
	loc     = "local";
	args    = r => ["--dereference", "--brief", "--keep-going", "--raw", "--", r.inFile()];
	post    = r =>
	{
		// OK.... so file does have the --keep-going flag but it isn't really designed to properly output multiple matches as several matches also output a 'continuation' of the match on a new line
		// We do some hacky trickery here to try and determine where one match ends and another begins, but it's not great. It mostly relies on there being a comma whenever a match 'continues'
		// This sort of wonky output formatting is in libmagic itself, so writing a custom file program to directly call into libmagic.so doesn't gain us anything
		// Without --raw then file has a BUG that outputs truncated data when it encounters certain characters like \r\n See: sample/text/txt/DORINFO1.DEF
		// The file source code itself is VERY messy and gross, so trying to modify/patch it to output a better seperator when --keep-going (MAGIC_CONTINUE) is used would be painful, I couldn't figure out where it's even happening at exactly
		// So in the end we just do our best here, knowing that we'll get some grossness in the detections for some files, but hopefully this will improve with time as I discover more edge cases. Sigh.
		// Other problematic files to use to test logic:
		//     archive/rawPartition/Madame X Game.bin
		//     archive/iso/The Girls of GLITZ.iso
		//     text/txt/2.emlx
		//	   archive/zip/neopnt21.zip		<-- This shows how bad file is. The '-  to extract' line is a continuation of the previous match, but the '-  Zip archive data' is a new match. We just can't really handle this, checking case of first letter is unsafe
		//     document/dBaseMultipleIndex/CLIENT.MDX

		r.meta.detections = [];
		let confidence = 100;
		let fileText =  r.stdout.trim();

		// First, replace things we know are the start of a new match
		fileText = fileText.replace(/\n- {2}/g, "§");

		// Next things we are pretty certain are just an extension of the match from the previous line, combine those up with the previous line match text
		fileText = fileText.replace(/\n[^ -]/g, "");
		fileText = fileText.replace(/\n- (.?),/g, "$1,");

		// Now handle remaining newline prefixes as a match seperator
		fileText = fileText.replace(/\n- /g, "§");

		if(fileText.includes("\n"))
			r.xlog.error`Unhandled newline in file output, add support for this edge case in detect/file.js: ${JSON.stringify(fileText)}`;

		for(const value of fileText.split("§").unique())
			r.meta.detections.push(Detection.create({value, from : "file", confidence : confidence--, file : r.f.input}));
	};
	renameOut = false;
}
