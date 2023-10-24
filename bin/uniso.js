import {xu} from "xu";
import {cmdUtil, fileUtil, runUtil, encodeUtil} from "xutil";
import {path, dateParse} from "std";
import {XLog} from "xlog";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input.iso> as an ISO and extracting into <outputDirPath>",
	opts    :
	{
		offset      : {desc : "If set, mount at the given offset", hasValue : true},
		block       : {desc : "If set, specify a given block size for the ISO image.", hasValue : true},
		hfs         : {desc : "If set, CD will be treated as HFS MAC cd"},
		hfsplus     : {desc : "If set, CD will be treated as HFS+ MAC cd"},
		nextstep    : {desc : "If set, CD will be treated as NeXTSTEP cd"},
		logLevel    : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "warn"},
		ts          : {desc : "Will be used as the fallback ts in case of messed up HFS dates", hasValue : true, defaultValue : Date.now()},
		macEncoding : {desc : "Specify the Mac encoding to decode HFS filenames. Valid: roman | japan", hasValue : true, defaultValue : "roman"},
		checkMount  : {desc : "If set, after mounting it will attempt to run ls on the mount and ensure there are no errors"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "ISO file path to extract", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});

const xlog = new XLog(argv.logLevel);

const IN_FILE_PATH = path.resolve(argv.inputFilePath);
const OUT_DIR_PATH = path.resolve(argv.outputDirPath);

const MOUNT_DIR_PATH = await fileUtil.genTempPath(undefined, "_uniso");
await Deno.mkdir(MOUNT_DIR_PATH);

async function extractNormalISO()
{
	xlog.info`Extracting ISO as Normal ISO...`;
		
	const mountArgs = [];
	if(argv.offset || argv.block)
		mountArgs.push("-o", `loop,ro${argv.offset ? `,offset=${argv.offset}` : ""}${argv.block ? `,block=${argv.block}` : ""}`);
	if(argv.nextstep)
		mountArgs.push("-t", "ufs", "-o", "ufstype=nextstep-cd");
	if(argv.hfsplus)
		mountArgs.push("-t", "hfsplus");

	await runUtil.run("sudo", ["mount", ...mountArgs, IN_FILE_PATH, MOUNT_DIR_PATH], {liveOutput : xlog.atLeast("debug")});

	const {stdout : mountStatus} = await runUtil.run("sudo", ["findmnt", "--output", "FSTYPE", "--noheadings", MOUNT_DIR_PATH]);

	// Sometimes an ISO's ISO9660 side is corrupt and fails to mount, then mount falls back automatically to the hfs section if there is one
	// But we don't want to use mount's built in HFS support, we explicitly handle HFS vs non HFS at a higher level, so we abort the mission here
	if(mountStatus.trim().toLowerCase().startsWith("hfs") && !argv.hfs && !argv.hfsplus)
	{
		xlog.warn`ISO failed to mount: ${mountStatus.trim()}`;
		return await runUtil.run("sudo", ["umount", MOUNT_DIR_PATH]);
	}

	if(argv.checkMount)
	{
		const {stderr} = await runUtil.run("ls", ["-R", MOUNT_DIR_PATH], {timeout : xu.SECOND*20});
		if(stderr.toLowerCase().includes("input/output error"))
		{
			xlog.warn`ISO has input/output errors: ${stderr}`;
			await runUtil.run("sudo", ["umount", MOUNT_DIR_PATH]);
			return;
		}
	}

	// ALERT! In node, we used to use cp instead of rsync, but I couldn't get the shell /bin/bash thing to work right with cp and sudo under Deno. So I use rsync instead, we'll see if that chokes on certain filenames or not
	//runUtil.run("sudo", ["cp", "--sparse=never", "--preserve=timestamps", "-r", "*", `"${OUT_DIR_PATH}/"`], {...RUN_OPTIONS, shell : "/bin/bash", cwd : MOUNT_DIR_PATH}, this);
	await runUtil.run("sudo", ["rsync", "-sa", `${MOUNT_DIR_PATH}/`, `${OUT_DIR_PATH}/`], {liveOutput : xlog.atLeast("debug")});

	await runUtil.run("sudo", ["umount", MOUNT_DIR_PATH]);
}

///////////////////////////////////////////////////////////////////////////
/////////////////////////////////// HFS ///////////////////////////////////
///////////////////////////////////////////////////////////////////////////

// All the hfsutils store their 'state' in a file written to home, we set the 'HOME' env to be our mount directory in order to not clobber other extractions taking place at the same time
const HFS_RUN_OPTIONS = {env : {"HOME" : MOUNT_DIR_PATH}};

async function extractHFSISO()
{
	xlog.info`Extracting ISO as HFS...`;

	const metadata = {fileMeta : {}};
	const filenameDecodeOpts = {processors : encodeUtil.macintoshProcessors.octal, region : argv.macEncoding};
	let volumeYear=null;
	const seenIds = new Set();

	const recurseHFS = async function recurseHFS(subPath)
	{
		await Deno.mkdir(path.join(OUT_DIR_PATH, subPath), {recursive : true});
		
		// get list
		const {stdout : entriesRaw} = await runUtil.run("hls", ["-albi"], HFS_RUN_OPTIONS);

		// copy out files
		const hlsRegex = /^\s*(?<id>\d+)\s+(?<type>[Fdf])i?\s+(?<fileType>[^/]+)?\/?(?<fileCreator>\S+).+(?<month>[A-Z][a-z]{2})\s+(?<day>[\s\d]\d)\s+(?<yearOrTime>\d\d:\d\d|\d{4})\s?(?<filename>.+)$/;
		const entries = entriesRaw.split("\n").filter(v => !!v).map(entryRaw => (entryRaw.match(hlsRegex) || {})?.groups);
		for(const entry of entries)
		{
			if(!entry?.type)
			{
				const {stdout : curpwdi} = await runUtil.run("hpwdi", [], HFS_RUN_OPTIONS);
				Deno.exit(xlog.error`Failed to get directory entry for curpwdi ${curpwdi.trim()} and subPath ${subPath} and entry ${entry} with entriesRaw: ${entriesRaw}`);
			}

			if(entry.type==="d")
				continue;
			
			entry.destFilePath = path.join(OUT_DIR_PATH, subPath, await encodeUtil.decodeMacintosh({data : entry.filename, ...filenameDecodeOpts}));

			// some files on HFS CD's have absurdly incorrect dates, like "Cool Demos/Demos/Troubled Souls Demo" on the Odyssey: Legend of Nemesis CD having a date of Jun 30, 1922
			// so for those, fall back to something sane
			const year = entry.yearOrTime.includes(":") ? volumeYear : +entry.yearOrTime;
			let ts = argv.ts;
			if(year && !isNaN(year) && year>=1972)
			{
				const month = {"jan" : 1, "feb" : 2, "mar" : 3, "apr" : 4, "may" : 5, "jun" : 6, "jul" : 7, "aug" : 8, "sep" : 9, "oct" : 10, "nov" : 11, "dec" : 12}[entry.month.toLowerCase()];
				const dateString = `${year}-${month.toString().padStart(2, "0")}-${entry.day.trim().padStart(2, "0")} 00:00:00`;
				ts = dateParse(dateString, "yyyy-MM-dd HH:mm:ss").getTime();
			}

			const safeFilePath = await fileUtil.genTempPath(OUT_DIR_PATH);

			// if we are a text file, we should always extract as raw and let programs further up the stack worry about decoding it properly. this way if a raw output text file is viewed on an actual Mac, it would render just fine
			await runUtil.run("hcopyi", [...(["text", "ttro"].includes(entry?.fileType?.toLowerCase()) ? ["-r"] : []), entry.id, safeFilePath], {...HFS_RUN_OPTIONS, liveOutput : true});
			const entryFileMeta = {};
			if(entry.fileType?.length)
				entryFileMeta.macFileType = entry.fileType;
			if(entry.fileCreator?.length && entry.fileCreator!=="/")
				entryFileMeta.macFileCreator = entry.fileCreator;
			if(Object.keys(entryFileMeta).length>0)
				metadata.fileMeta[path.relative(OUT_DIR_PATH, entry.destFilePath)] = entryFileMeta;

			try
			{
				await Deno.rename(safeFilePath, entry.destFilePath);
				await Deno.utime(entry.destFilePath, Math.floor(ts/xu.SECOND), Math.floor(ts/xu.SECOND));
			}
			catch(err)
			{
				console.error(`Failed to copy id ${entry.id} to ${entry.destFilePath} due to ${err}`);
			}
		}

		// now handle our directories
		for(const entry of entries)
		{
			if(entry.type!=="d")
				continue;
			
			await runUtil.run("hcdi", [entry.id], HFS_RUN_OPTIONS);
			const {stdout} = await runUtil.run("hpwdi", [], HFS_RUN_OPTIONS);
			const idAfter = stdout.trim();

			if(seenIds.has(idAfter))
			{
				if((+entry.id)!==(+idAfter))
					console.error(`Failed to change into directory id ${entry.id} with name ${entry.filename} inside of ${subPath}`);
				else
					console.error(`Skipping dir ${+entry.id} ${entry.filename} inside of ${subPath} as we've already seen it`);
				continue;
			}
			
			seenIds.add(idAfter);
			await recurseHFS(path.join(subPath, await encodeUtil.decodeMacintosh({data : entry.filename, ...filenameDecodeOpts})));
			await runUtil.run("hcd", ["::"], HFS_RUN_OPTIONS);
		}
	};

	await runUtil.run("hmount", [IN_FILE_PATH], HFS_RUN_OPTIONS);

	// Get our volume creation year to use as the default year as some files only specify the time and not the year (WWDC.iso)
	const {stdout : volInfo} = await runUtil.run("hvol", [], HFS_RUN_OPTIONS);
	if(volInfo.includes("No known volumes"))
		return;

	const volCreationParts = (volInfo.match(/Volume was created on (?<dayOfWeek>[A-Z][a-z]{2})\s(?<month>[A-Z][a-z]{2})\s(?<day>[\d\s]\d)\s(?<time>\d\d:\d\d:\d\d)\s(?<year>\d{4})/) || {})?.groups;
	volumeYear = +(volCreationParts?.year || new Date((await Deno.stat(IN_FILE_PATH)).mtime).getFullYear());
	
	await recurseHFS("");
	await runUtil.run("humount", [IN_FILE_PATH], HFS_RUN_OPTIONS);
	await fileUtil.unlink(path.join(MOUNT_DIR_PATH, ".hcwd"));

	if(Object.keys(metadata.fileMeta).length>0)
		console.log(JSON.stringify(metadata));
}

// main
if(argv.hfs)	// eslint-disable-line unicorn/prefer-ternary
	await extractHFSISO();
else
	await extractNormalISO();

const {stdout : whoami} = await runUtil.run("whoami", []);
await runUtil.run("sudo", ["chown", `${whoami.trim()}:users`, OUT_DIR_PATH]);
await runUtil.run("chmod", ["777", OUT_DIR_PATH]);
await fileUtil.unlink(MOUNT_DIR_PATH, {recursive : true});
