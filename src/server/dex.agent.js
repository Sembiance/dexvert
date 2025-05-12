import {xu} from "xu";
import {dexvert} from "../dexvert.js";
import {identify} from "../identify.js";
import {XLog} from "xlog";
import {path} from "std";
import {DexFile} from "../DexFile.js";
import {init as initPrograms, programChanged} from "../program/programs.js";
import {init as initFormats, formatChanged, formats} from "../format/formats.js";
import {agentInit} from "AgentPool";

await initPrograms();
await initFormats();

const slowExtensions = new Set(Object.values(formats).filter(format => format.slow && format.ext?.length).flatMap(format => format.ext));

await agentInit(async ({inputFilePath, outputDirPath, logLevel="error", fileMeta, op, change={}, timeout, dexvertOptions={}}) =>
{
	if(["formatChange", "programChange"].includes(op))
	{
		const changeLogLines = [];
		const changeXLog = new XLog("info", {logger : v => changeLogLines.push(v)});
		if(op==="formatChange")
			await formatChanged(change, changeXLog);
		if(op==="programChange")
			await programChanged(change, changeXLog);
		return {changeResult : changeLogLines.join("\n")};
	}

	timeout ||= xu.HOUR*(slowExtensions.has(path.extname(inputFilePath)?.toLowerCase()) ? 2 : 1);	// for slow formats, if we match the extension, give a little more time

	const xlog = new XLog(logLevel);

	let r = null;
	try
	{
		const twigDiskFile = await DexFile.create(inputFilePath);
		if(fileMeta)
			twigDiskFile.meta = fileMeta;

		const tryOp = async () =>
		{
			// since tryOp is async but we fire and forget it, we need to have a try/catch here to catch any exceptions otherwise it crashes the whole process with an uncaught exception error
			try
			{
				if(op==="dexid")
				{
					r ||= await identify(twigDiskFile, {xlog});
				}
				else if(op==="dexvert")
				{
					const dexState = await dexvert(twigDiskFile, await DexFile.create(outputDirPath), {xlog, ...dexvertOptions});
					r ||= dexState ? {json : dexState.serialize(), pretty : dexState.pretty()} : `dexvert failed to return a dexState object for inputFilePath ${inputFilePath} and outputDirPath ${outputDirPath}`;
				}
			}
			catch(suberr)
			{
				r ||= suberr.stack;
			}
		};

		let tooLongTimer;
		tooLongTimer = setTimeout(() =>
		{
			tooLongTimer = null;
			r ||= `${op} twigDiskFilePath ${xu.bracket(inputFilePath)} took too long (>${timeout.msAsHumanReadable()}) to process and was aborted (outputDirPath ${outputDirPath})`;
		}, timeout);
		tryOp();
		await xu.waitUntil(() => !!r);
		if(tooLongTimer)
			clearTimeout(tooLongTimer);
	}
	catch(err)
	{
		r = err.stack;
	}

	const fullResult = {};
	fullResult[typeof r==="string" ? "err" : "r"] = r;
	return fullResult;
});


