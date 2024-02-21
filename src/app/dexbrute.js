import {xu, fg} from "xu";
import {XLog} from "xlog";
import {cmdUtil, fileUtil, printUtil} from "xutil";
import {dexvert} from "../dexvert.js";
import {programs, init as initPrograms} from "../program/programs.js";
import {formats, init as initFormats} from "../format/formats.js";
import {families} from "../family/families.js";
import {DexFile} from "../DexFile.js";
import {Format} from "../Format.js";
import {path} from "std";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexbrute",
	version : "1.0.0",
	desc    : "Processes <inputFilePath> trying every safe program on it and saving results in <outputDirPath>",
	opts    :
	{
		allowUnsafe : {desc : "Run all programs, even those marked as unsafe"},
		family      : {desc : "Restrict programs to this family (comma delimited list allowed)", hasValue : true},
		serial      : {desc : "Run the programs serially..."},
		debug       : {desc : "Debug mode"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "The path to the file to process", required : true},
		{argid : "outputDirPath", desc : "Output directory path", required : true}
	]});

const xlog = new XLog("info");

await initPrograms(xlog);
await initFormats(xlog);

const EXCLUDE_FAMILIES = ["detect", "meta", "other", "post"];
const PROGRAM_BASE_PATH = path.join(import.meta.dirname, "..", "program");
const programFamilies = (await fileUtil.tree(PROGRAM_BASE_PATH, {nodir : true, regex : /.+\/.+\.js$/i})).map(v => path.relative(PROGRAM_BASE_PATH, v)).reduce((o, v) =>
{
	const familyid = v.split("/")[0];
	if(!Object.hasOwn(o, familyid))
		o[familyid] = [];
	o[familyid].push(path.basename(v, ".js"));
	return o;
}, {});

await fileUtil.unlink(path.resolve(argv.outputDirPath), {recursive : true});
await Deno.mkdir(path.resolve(argv.outputDirPath));

const inputFile = await DexFile.create(argv.inputFilePath);

await Object.entries(programs).parallelMap(async ([programid, program]) =>
{
	const familyid = Object.entries(programFamilies).find(([, progs]) => progs.includes(programid))[0];
	if(EXCLUDE_FAMILIES.includes(familyid))
		return;
	
	if(argv.family && !argv.family.split(",").includesAny([familyid, ...(program.bruteFlags ? Object.keys(program.bruteFlags) : [])]))
		return;
	
	if(program.unsafe && !argv.allowUnsafe)
		return;

	const formatid = `program${programid}`;

	class ProgramFormat extends Format
	{
		name = programid;
		converters = [programid];
	}

	const programFlag = argv?.family?.split(",").find(v => !!program.bruteFlags?.[v]) || {};

	const format = ProgramFormat.create(families[familyid]);
	format.formatid = formatid;
	formats[formatid] = format;

	const outputDirPath = path.join(argv.outputDirPath, familyid, programid);
	await Deno.mkdir(outputDirPath, {recursive : true});
	const outputDir = await DexFile.create(outputDirPath);

	if(argv.serial)
		printUtil.stdoutWrite(`Program ${familyid}/${programid} `);
	const dexState = await dexvert(inputFile, outputDir, {xlog : (argv.debug ? xlog : xlog.clone("none")), programFlag, asFormat : `${familyid}/${formatid}`});
	const outputFiles = dexState.f.files.output || [];
	if(outputFiles.length>0)
	{
		xlog.info`${!argv.serial ? `Program ${familyid}/${programid} ` : ""}produced ${outputFiles.length} files`;
	}
	else
	{
		xlog.info`${!argv.serial ? `Program ${familyid}/${programid} ` : ""}${fg.red("none")}`;
		await fileUtil.unlink(outputDirPath, {recursive : true});
	}
}, argv.serial ? 1 : 10);

