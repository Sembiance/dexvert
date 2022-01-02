import {xu} from "xu";
import {cmdUtil, fileUtil, runUtil} from "xutil";
import {path} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input.iso> as an ISO and extracting into <outputDirPath>",
	opts    :
	{
		offset : {desc : "If set, mount at the given offset", hasValue : true},
		hfs    : {desc : "If set, CD will be treated as HFS MAC cd"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "ISO file path to extract", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});

const IN_FILE_PATH = path.resolve(argv.inputFilePath);
const OUT_DIR_PATH = path.resolve(argv.outputDirPath);

const MOUNT_DIR_PATH = await fileUtil.genTempPath(undefined, "_uniso");
await Deno.mkdir(MOUNT_DIR_PATH);

async function extractNormalISO()
{
	const mountArgs = [];
	if(argv.offset)
		mountArgs.push("-o", `loop,offset=${argv.offset}`);

	await runUtil.run("sudo", ["mount", ...mountArgs, IN_FILE_PATH, MOUNT_DIR_PATH]);

	const {stdout : mountStatus} = await runUtil.run("sudo", ["findmnt", "--output", "FSTYPE", "--noheadings", MOUNT_DIR_PATH]);

	// Sometimes an ISO's ISO9660 side is corrupt and fails to mount, then mount falls back automatically to the hfs section if there is one
	// Also, sometimes we can't detect ahead of time in dexvert that it is an HFS ISO, but when we mount it, we discover it is
	// Either way, we want to use our special extractHFSISO() method for handling HFS ISOs, so we unmount it and use extractHFSISO instead
	if(mountStatus.trim().toLowerCase()==="hfs")
	{
		await runUtil.run("sudo", ["umount", MOUNT_DIR_PATH]);
		await extractHFSISO();
		return;
	}

	// ALERT! In node, we used to use cp instead of rsync, but I couldn't get the shell /bin/bash thing to work right with cp and sudo under Deno. So I use rsync instead, we'll see if that chokes on certain filenames or not
	//runUtil.run("sudo", ["cp", "--sparse=never", "--preserve=timestamps", "-r", "*", `"${OUT_DIR_PATH}/"`], {...RUN_OPTIONS, shell : "/bin/bash", cwd : MOUNT_DIR_PATH}, this);
	await runUtil.run("sudo", ["rsync", "-sa", `${MOUNT_DIR_PATH}/`, `${OUT_DIR_PATH}/`]);

	await runUtil.run("sudo", ["umount", MOUNT_DIR_PATH]);
}

///////////////////////////////////////////////////////////////////////////
/////////////////////////////////// HFS ///////////////////////////////////
///////////////////////////////////////////////////////////////////////////
const HFS_OCTAL_TO_UTF8 = {"80" : 0x00C4, "81" : 0x00C5, "82" : 0x00C7, "83" : 0x00C9, "84" : 0x00D1, "85" : 0x00D6, "86" : 0x00DC, "87" : 0x00E1, "88" : 0x00E0, "89" : 0x00E2, "8A" : 0x00E4, "8B" : 0x00E3, "8C" : 0x00E5, "8D" : 0x00E7, "8E" : 0x00E9, "8F" : 0x00E8, "90" : 0x00EA, "91" : 0x00EB, "92" : 0x00ED, "93" : 0x00EC, "94" : 0x00EE, "95" : 0x00EF, "96" : 0x00F1, "97" : 0x00F3, "98" : 0x00F2, "99" : 0x00F4, "9A" : 0x00F6, "9B" : 0x00F5, "9C" : 0x00FA, "9D" : 0x00F9, "9E" : 0x00FB, "9F" : 0x00FC, "A0" : 0x2020, "A1" : 0x00B0, "A2" : 0x00A2, "A3" : 0x00A3, "A4" : 0x00A7, "A5" : 0x2022, "A6" : 0x00B6, "A7" : 0x00DF, "A8" : 0x00AE, "A9" : 0x00A9, "AA" : 0x2122, "AB" : 0x00B4, "AC" : 0x00A8, "AD" : 0x2260, "AE" : 0x00C6, "AF" : 0x00D8, "B0" : 0x221E, "B1" : 0x00B1, "B2" : 0x2264, "B3" : 0x2265, "B4" : 0x00A5, "B5" : 0x00B5, "B6" : 0x2202, "B7" : 0x2211, "B8" : 0x220F, "B9" : 0x03C0, "BA" : 0x222B, "BB" : 0x00AA, "BC" : 0x00BA, "BD" : 0x2126, "BE" : 0x00E6, "BF" : 0x00F8, "C0" : 0x00BF, "C1" : 0x00A1, "C2" : 0x00AC, "C3" : 0x221A, "C4" : 0x0192, "C5" : 0x2248, "C6" : 0x2206, "C7" : 0x00AB, "C8" : 0x00BB, "C9" : 0x2026, "CA" : 0x00A0, "CB" : 0x00C0, "CC" : 0x00C3, "CD" : 0x00D5, "CE" : 0x0152, "CF" : 0x0153, "D0" : 0x2013, "D1" : 0x2014, "D2" : 0x201C, "D3" : 0x201D, "D4" : 0x2018, "D5" : 0x2019, "D6" : 0x00F7, "D7" : 0x25CA, "D8" : 0x00FF, "D9" : 0x0178, "DA" : 0x2044, "DB" : 0x00A4, "DC" : 0x2039, "DD" : 0x203A, "DE" : 0xFB01, "DF" : 0xFB02, "E0" : 0x2021, "E1" : 0x00B7, "E2" : 0x201A, "E3" : 0x201E, "E4" : 0x2030, "E5" : 0x00C2, "E6" : 0x00CA, "E7" : 0x00C1, "E8" : 0x00CB, "E9" : 0x00C8, "EA" : 0x00CD, "EB" : 0x00CE, "EC" : 0x00CF, "ED" : 0x00CC, "EE" : 0x00D3, "EF" : 0x00D4, "F0" : 0xF8FF, "F1" : 0x00D2, "F2" : 0x00DA, "F3" : 0x00DB, "F4" : 0x00D9, "F5" : 0x0131, "F6" : 0x02C6, "F7" : 0x02DC, "F8" : 0x00AF, "F9" : 0x02D8, "FA" : 0x02D9, "FB" : 0x02DA, "FC" : 0x00B8, "FD" : 0x02DD, "FE" : 0x02DB, "FF" : 0x02C7};	// eslint-disable-line max-len
const HFS_CHAR_TO_UTF8 = {" " : " ", t : "⇥", r : "↵", n : "␤"};
// All the hfsutils store their 'state' in a file written to home, we set the 'HOME' env to be our mount directory in order to not clobber other extractions taking place at the same time
const HFS_RUN_OPTIONS = {env : {"HOME" : MOUNT_DIR_PATH}};

// will convert an hfsFilename to a UTF-8 equlivant
function hfsFilenameToUTF8(hfsFilename)
{
	let match = null;
	let utfFilename = hfsFilename.replaceAll("/", "⁄");	// Mac files can contain forward slashes, so we replace them with a unicode fraction slash
	do
	{
		match = (utfFilename.match(/\\(?<code>\d{3})/) || {}).groups;
		if(match)
		{
			const charCode = HFS_OCTAL_TO_UTF8[Number.parseInt(match.code, 8).toString(16).padStart(2, "0").toUpperCase()] || 0x25A1;
			utfFilename = utfFilename.replaceAll(`\\${match.code}`, String.fromCharCode(charCode));
			continue;
		}

		match = (utfFilename.match(/\\(?<letter>.)/) || {}).groups;
		if(match)
			utfFilename = utfFilename.replaceAll(`\\${match.letter}`, HFS_CHAR_TO_UTF8[match.letter] || "□");
	} while(match);

	return utfFilename;
}

async function hcopyFile(src, dest)
{
	const safeFilePath = await fileUtil.genTempPath(OUT_DIR_PATH);

	// Wasn't able to figure out how to escape properly the \r sequence found in so many HFS filenames, without resorting to calling out to a bash script that does some fancy eval magic I'll never understand
	// Sadly, due to the use of eval it horribly handles weird quotes and other things, which isn't a problem for 'src' since hls will binary escape those, but it is an issue for the dest
	// So we need to copy to a temp safe filename and then rename it
	await runUtil.run(path.join(xu.dirname(import.meta), "dexhcopyfile"), [src.replaceAll("'", "\\047"), safeFilePath], HFS_RUN_OPTIONS);

	await Deno.rename(safeFilePath, dest);
}

/* Uncomment this if I end up splitting files into data/resource fork again
function fixUnarFilename(unarFilename)
{
	// unar ends up creating it's own escaping scheme that we need to fix.

	// Sometimes it's just the raw character values
	const CHAR_REPLACEMENT = {"\t" : "⇥", "\r" : "↵", "\n" : "␤"};
	let fixedFilename = unarFilename.split("").map(c =>
	{
		if(Object.hasOwn(CHAR_REPLACEMENT, c))
			return CHAR_REPLACEMENT[c];
		
		if(c.charCodeAt(0)<0x20)
			return "□";
		
		return c;
	}).join("");

	// Other times it's %xx encoded
	let match = null;
	do
	{
		match = (fixedFilename.match(/%(?<code>[A-Fa-f\d]{2})/) || {}).groups;
		if(match)
			fixedFilename = fixedFilename.replaceAll(`%${match.code}`, String.fromCharCode(HFS_OCTAL_TO_UTF8[match.code.toUpperCase()] || 0x25A1));
	} while(match);

	return fixedFilename;
}*/

// This will extract the HFS CD and automatically convert characters from Mac Standard Roman to UTF8: https://github.com/Distrotech/hfsutils/blob/master/doc/charset.txt
async function extractHFSISO()
{
	const HCDNUM_BIN = path.join(xu.dirname(import.meta), "hcdnum");

	const recurseHFS = async function recurseHFS(subPath)
	{
		await Deno.mkdir(path.join(OUT_DIR_PATH, subPath), {recursive : true});
		
		// get list
		const {stdout : entriesRaw} = await runUtil.run("hls", ["-alb"], HFS_RUN_OPTIONS);

		// copy out files
		const entries = entriesRaw.trim().split("\n").filter(v => !!v).map(entryRaw => (entryRaw.match(/^(?<type>f|d)i?\s.+(?<year>\d{4})\s(?<filename>.+)$/) || {}).groups);
		for(const entry of entries)
		{
			if(entry.type!=="f")
				continue;
			
			entry.destFilePath = path.join(OUT_DIR_PATH, subPath, hfsFilenameToUTF8(entry.filename));
			await hcopyFile(entry.filename, entry.destFilePath);
		}

		// This code used to use 'unar' to split each file into two potential files, one containing the datafork and one containing the resource fork (ending in .rsrc)
		// First, I no longer like doing this, as macBinary support within dexvert itself has been enhanced
		// Also I like to keep the original filenames, which are lost if I use unar to split the files
		// Lastly, there is some sort of BUG in this code below with deno. Works fine if I dextry directly resultant Mac User Ultimate Mac Companion 1996.ugh file, but doesn't work in the bchunk chain to dexvert
		// time to split our data fork and resource forks
		/*await entries.parallelMap(async entry =>
		{
			if(entry.type!=="f")
				return;

			const tmpUnpackDirPath = await fileUtil.genTempPath(OUT_DIR_PATH);
			await Deno.mkdir(tmpUnpackDirPath);
			await runUtil.run("unar", ["-f", "-D", "-o", tmpUnpackDirPath, entry.destFilePath]);

			const unpackedFilePaths = await fileUtil.tree(tmpUnpackDirPath, {nodir : true});
			if(unpackedFilePaths.length>0)
			{
				// We delete the original first, because what we extracted out may contain a data fork file with same name but encoded differently sometimes, so it's best just to delete the original 'combined' file
				await fileUtil.unlink(entry.destFilePath);

				// NOTE This doesn't check for clobbers with other pre-existing files that might be named the same as what unar produced (such as Input and Input.rsrc)
				// If this is encountered in the future, we could ensure the file doesn't already exist and create a backup unique name if needed
				await unpackedFilePaths.parallelMap(async unpackedFilePath => await fileUtil.move(unpackedFilePath, path.join(path.dirname(entry.destFilePath), fixUnarFilename(path.basename(unpackedFilePath)))));
			}

			await fileUtil.unlink(tmpUnpackDirPath, {recursive : true});
		});*/

		// now handle our directories
		for(const [i, entry] of Object.entries(entries))
		{
			if(entry.type==="f")
				continue;
			
			const lineNum = +i;
			
			await runUtil.run(HCDNUM_BIN, [`${(lineNum+1)}`], HFS_RUN_OPTIONS);
			await recurseHFS(path.join(subPath, hfsFilenameToUTF8(entry.filename)));
			await runUtil.run("hcd", ["::"], HFS_RUN_OPTIONS);
		}
	};

	await runUtil.run("hmount", [IN_FILE_PATH], HFS_RUN_OPTIONS);
	await recurseHFS("");
	await runUtil.run("humount", [IN_FILE_PATH], HFS_RUN_OPTIONS);
	await fileUtil.unlink(path.join(MOUNT_DIR_PATH, ".hcwd"));
}

// main
await (argv.hfs ? extractHFSISO() : extractNormalISO());
await fileUtil.unlink(MOUNT_DIR_PATH, {recursive : true});
