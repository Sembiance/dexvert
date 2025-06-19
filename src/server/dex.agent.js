import {xu} from "xu";
import {dexvert} from "../dexvert.js";
import {identify} from "../identify.js";
import {XLog} from "xlog";
import {DexFile} from "../DexFile.js";
import {init as initPrograms, programChanged} from "../program/programs.js";
import {init as initFormats, formatChanged} from "../format/formats.js";
import {agentInit} from "AgentPool";

await initPrograms();
await initFormats();

const logLines = [];

await agentInit(async ({inputFilePath, outputDirPath, logLevel="error", fileMeta, op, change={}, timeout, dexvertOptions={}}) =>
{
	logLines.clear();
	const xlog = new XLog(logLevel, {alwaysEcho : true, logger : line => logLines.push(line.decolor())});
	xlog.info`dex.agent.js: handling op ${op} for inputFilePath: ${inputFilePath}  outputDirPath: ${outputDirPath}  timeout: ${timeout}`;

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


	timeout ||= xu.HOUR*2;


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
					xlog.info`dex.agent.js: calling identify`;
					r ||= await identify(twigDiskFile, {xlog});
					xlog.info`dex.agent.js: identify completed`;
				}
				else if(op==="dexvert")
				{
					xlog.info`dex.agent.js calling dexvert`;
					const dexState = await dexvert(twigDiskFile, await DexFile.create(outputDirPath), {xlog, ...dexvertOptions});
					xlog.info`dex.agent.js: dexvert completed`;
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
			xlog.info`dex.agent.js: timed out waiting for 'r'`;
			r ||= `${op} twigDiskFilePath ${xu.bracket(inputFilePath)} took too long (>${timeout.msAsHumanReadable()}) to process and was aborted (outputDirPath ${outputDirPath})`;
		}, timeout);
		tryOp();
		xlog.info`dex.agent.js: waiting for 'r' to be set`;
		await xu.waitUntil(() => !!r);
		xlog.info`dex.agent.js: done waiting for 'r' to be set`;
		if(tooLongTimer)
			clearTimeout(tooLongTimer);
	}
	catch(err)
	{
		r = err.stack;
	}

	const fullResult = {};
	fullResult[typeof r==="string" ? "err" : "r"] = r;

	xlog.info`dex.agent.js: returning fullResult`;
	return fullResult;
}, () => Array.from(logLines));
