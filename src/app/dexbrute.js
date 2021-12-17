import {xu, fg} from "xu";
import {cmdUtil, fileUtil} from "xutil";
import {dexvert} from "../dexvert.js";
import {programs} from "../program/programs.js";
import {formats} from "../format/formats.js";
import {families} from "../family/families.js";
import {DexFile} from "../DexFile.js";
import {Identification} from "../Identification.js";
import {Format} from "../Format.js";
import {path} from "std";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexbrute",
	version : "1.0.0",
	desc    : "Processes <inputFilePath> trying every safe program on it and saving results in <outputDirPath>",
	opts    :
	{
		family : {desc : "Restrict programs to this family (comma delimited list allowed)", hasValue : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "The path to the file to convert", required : true},
		{argid : "outputDirPath", desc : "Output directory path", required : true}
	]});

const xlog = xu.xLog("info");

const EXCLUDE_FAMILIES = ["detect", "meta", "other", "post"];
const PROGRAM_BASE_PATH = path.join(xu.dirname(import.meta), "..", "program");
const programFamilies = (await fileUtil.tree(PROGRAM_BASE_PATH, {nodir : true, regex : /.+\/.+\.js$/i})).map(v => path.relative(PROGRAM_BASE_PATH, v)).reduce((o, v) =>	// eslint-disable-line unicorn/prefer-object-from-entries
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
	
	if(argv.family && !argv.family.split(",").includes(familyid))
		return;
	
	if(program.unsafe)
		return;

	const formatid = `program${programid}`;

	class ProgramFormat extends Format
	{
		unsupported = true;
		name = programid;
		converters = [programid];
	}

	const format = ProgramFormat.create(families[familyid]);
	format.formatid = formatid;
	formats[formatid] = format;

	const outputDirPath = path.join(argv.outputDirPath, familyid, programid);
	await Deno.mkdir(outputDirPath, {recursive : true});
	const outputDir = await DexFile.create(outputDirPath);

	const dexState = await dexvert(inputFile, outputDir, {xlog : xlog.clone("none"), asId : Identification.create({from : "dexvert", family : familyid, formatid, magic : programid, matchType : "magic", confidence : 100})});
	const outputFiles = dexState.f.files.output || [];
	if(outputFiles.length>0)
	{
		xlog.info`Program ${familyid}/${programid} produced ${outputFiles.length} files`;
	}
	else
	{
		xlog.info`Program ${familyid}/${programid} ${fg.red("none")}`;
		await fileUtil.unlink(outputDirPath, {recursive : true});
	}
}, 10);

