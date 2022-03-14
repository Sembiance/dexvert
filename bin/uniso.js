import {xu} from "xu";
import {cmdUtil, fileUtil, runUtil, encodeUtil} from "xutil";
import {path, dateParse} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input.iso> as an ISO and extracting into <outputDirPath>",
	opts    :
	{
		offset     : {desc : "If set, mount at the given offset", hasValue : true},
		hfs        : {desc : "If set, CD will be treated as HFS MAC cd"},
		ts         : {desc : "Will be used as the fallback ts in case of messed up HFS dates", hasValue : true, defaultValue : Date.now()},
		checkMount : {desc : "If set, after mounting it will attempt to run ls on the mount and ensure there are no errors"}
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

	if(argv.checkMount)
	{
		const {stderr} = await runUtil.run("ls", ["-R", MOUNT_DIR_PATH]);
		if(stderr.toLowerCase().includes("input/output error"))
		{
			await runUtil.run("sudo", ["umount", MOUNT_DIR_PATH]);
			return;
		}
	}

	// ALERT! In node, we used to use cp instead of rsync, but I couldn't get the shell /bin/bash thing to work right with cp and sudo under Deno. So I use rsync instead, we'll see if that chokes on certain filenames or not
	//runUtil.run("sudo", ["cp", "--sparse=never", "--preserve=timestamps", "-r", "*", `"${OUT_DIR_PATH}/"`], {...RUN_OPTIONS, shell : "/bin/bash", cwd : MOUNT_DIR_PATH}, this);
	await runUtil.run("sudo", ["rsync", "-sa", `${MOUNT_DIR_PATH}/`, `${OUT_DIR_PATH}/`]);

	await runUtil.run("sudo", ["umount", MOUNT_DIR_PATH]);
}

///////////////////////////////////////////////////////////////////////////
/////////////////////////////////// HFS ///////////////////////////////////
///////////////////////////////////////////////////////////////////////////
const HFS_OCTAL_TO_UTF8 = Object.fromEntries(encodeUtil.MACOS_ROMAN_EXTENDED.map((v, i) => ([(128+i).toString(16).toUpperCase(), v.charCodeAt(0)])));
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
		const entries = entriesRaw.split("\n").filter(v => !!v).map(entryRaw => (entryRaw.match(/^(?<type>[Fdf])i?\s.+(?<month>[A-Z][a-z]{2})\s+(?<day>[\s\d]\d)\s+(?<year>\d{4})\s(?<filename>.+)$/) || {}).groups);
		for(const entry of entries)
		{
			if(entry.type==="d")
				continue;
			
			entry.destFilePath = path.join(OUT_DIR_PATH, subPath, hfsFilenameToUTF8(entry.filename));
			await hcopyFile(entry.filename, entry.destFilePath);

			// some files on HFS CD's have absurdly incorrect dates, like "Cool Demos/Demos/Troubled Souls Demo" on the Odyssey: Legend of Nemesis CD having a date of Jun 30, 1922
			// so for those, fall back to something sane
			const year = +entry.year;
			let ts = argv.ts;
			if(year && !isNaN(year) && year>=1972)
			{
				const month = {"jan" : 1, "feb" : 2, "mar" : 3, "apr" : 4, "may" : 5, "jun" : 6, "jul" : 7, "aug" : 8, "sep" : 9, "oct" : 10, "nov" : 11, "dec" : 12}[entry.month.toLowerCase()];
				const dateString = `${entry.year}-${month.toString().padStart(2, "0")}-${entry.day.trim().padStart(2, "0")} 00:00:00`;
				ts = dateParse(dateString, "yyyy-MM-dd HH:mm:ss").getTime();
			}
			
			await Deno.utime(entry.destFilePath, Math.floor(ts/xu.SECOND), Math.floor(ts/xu.SECOND));
		}

		// now handle our directories
		for(const [i, entry] of Object.entries(entries))
		{
			if(entry.type!=="d")
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
if(argv.hfs)	// eslint-disable-line unicorn/prefer-ternary
	await extractHFSISO();
else
	await extractNormalISO();
await fileUtil.unlink(MOUNT_DIR_PATH, {recursive : true});
