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
		//     archive/iso/The Girls of GLITZ.iso
		//     archive/macBinary/Click
		//     archive/rawPartition/Madame X Game.bin
		//	   archive/zip/neopnt21.zip		<-- This shows how bad 'file' is. The '-  to extract' line is a continuation of the previous match, but the '-  Zip archive data' is a new match. We can't really handle this as checking case of 1st letter is unsafe
		//     archive/zip/wresv111.zip
		//     document/dBaseMultipleIndex/CLIENT.MDX
		//     document/dbf/NUMEROS.DBF
		//     document/dbf/STAMPS.DAT
		//     executable/amigaExe/PowerPacker.pp
		//     executable/elf/D3D.UC
		//     image/gif/eb399.gif
		//     text/txt/2.emlx
		//     other/unknown/Bonus1.bin

		r.meta.detections = [];
		let confidence = 100;
		let fileText =  r.stdout.trim();
		r.xlog.trace`START fileText:\n${fileText}`;

		// Single-line edgecases: These should always remove the newline and include the next line as part of the match
		const SINGLE_LINE_PREFIXES =
		[
			[/^ERROR: \n- /, "ERROR: "]
		];
		for(const [prefexRegexp, prefixReplacement] of SINGLE_LINE_PREFIXES)
			fileText = fileText.replace(prefexRegexp, prefixReplacement);
		r.xlog.trace`A fileText:\n${fileText}`;

		// Multi-line edgecases. First item of the array is the prefix and the second is a list of possible subsequent line prefixes that are a continuation of the match
		const MULTI_LINE_PREFIXES =
		[
			[["Apollo", "dBase", "FoxBase", "Visual FoxPro", "VISUAL OBJECTS", "xBase"], ["DBF", "MDX", "DataBaseContainer"]],
			["BIOS", "device="],
			[["COFF", "MS-DOS executable"], "for "],
			[["Mach-O", "] ["], ["armv7", "bundle", "current ar", "executable", "dSYM", "dynamic linker", "dynamically linked", "fixed", "hppa", "i386", "i486", "kext", "object", "m68k", "ppc", "preload", "SPARC", "x86"]],
			["PGP symmetric key encrypted data", "salted"],
			["Zip archive data, made by", ["Amiga", "OpenVMS", "UNIX", "VM/CMS", "OS/2", "Macintosh", "MVS", "Acorn Risc", "BeOS", "Tandem", "Atari ST", "Z-System", "CP/M", "Windows NTFS", "VSE", "VFAT", "alternate MVS", "OS/400", "OS X"]],
			["Apple QuickTime move", "non-streamed"]
		];
		for(const [prefixes, subfixes] of MULTI_LINE_PREFIXES)
		{
			for(const prefix of Array.force(prefixes))
			{
				for(const subfix of Array.force(subfixes))
					fileText = fileText.replace(new RegExp(`(\n-  ?)?${prefix[0]}([^\n]+)\n-  ?${subfix}`, "g"), `$1${prefix[0]}$2 ${subfix}`);
			}
		}
		r.xlog.trace`B fileText:\n${fileText}`;

		// Generic prefix edgecases. Magics where a '-  ?<text>' is a continuation and not a new match. Since some of them start with '-  ' we need to deal with this first before the next step
		const PREFIXES =
		[
			"at byte",
			"block device driver",
			"COFF",
			"filetype=",
			"for ",
			"last modified",
			"of \\d+ bytes",
			"to extract,",
			"version \\d",
			`[;:)(\\]["']`
		];
		for(const prefix of PREFIXES)
			fileText = fileText.replace(new RegExp(`\n-  ?(${prefix})`, "g"), " $1");
		r.xlog.trace`C fileText:\n${fileText}`;

		// Replace things that are "usually" the start of a new match (but not always, sigh)
		fileText = fileText.replace(/\n- {2}/g, "§");
		r.xlog.trace`D fileText:\n${fileText}`;

		// Things we are pretty sure are just an extension of the match from the previous line, combine those up with the previous line match text
		fileText = fileText.replace(/\n[^ -]/g, "");
		r.xlog.trace`E fileText:\n${fileText}`;

		fileText = fileText.replace(/\n- (.?),/g, "$1,");
		r.xlog.trace`F fileText:\n${fileText}`;

		// Now handle remaining newline prefixes as a match seperator
		fileText = fileText.replace(/\n- /g, "§");
		r.xlog.trace`G fileText:\n${fileText}`;

		fileText = fileText.replace(/§§/g, "§");
		r.xlog.trace`Z fileText:\n${fileText}`;

		if(fileText.includes("\n"))
			r.xlog.error`Unhandled newline in file output, add support for this edge case in detect/file.js: ${JSON.stringify(fileText)}`;

		for(const value of fileText.split("§").unique())
			r.meta.detections.push(Detection.create({value : value.trim(), from : "file", confidence : confidence--, file : r.f.input}));
	};
	renameOut = false;
}
