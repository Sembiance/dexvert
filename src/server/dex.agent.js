import {xu} from "xu";
import {dexvert} from "../dexvert.js";
import {identify} from "../identify.js";
import {XLog} from "xlog";
import {DexFile} from "../DexFile.js";
import {initRegistry} from "../dexUtil.js";
import {programChanged} from "../program/programs.js";
import {formatChanged} from "../format/formats.js";
import {agentInit} from "AgentPool";

await initRegistry();

const logLines = [];
const xlog = new XLog("error", {alwaysEcho : true, logger : line => logLines.push(line.decolor())});

await agentInit(async ({inputFilePath, outputDirPath, logLevel="error", fileMeta, op, change={}, dexvertOptions={}}) =>
{
	logLines.clear();
	xlog.level = logLevel;
	
	xlog.info`dex.agent.js: handling op ${op} for inputFilePath: ${inputFilePath}  outputDirPath: ${outputDirPath}`;

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

	let r = null;
	try
	{
		const twigDiskFile = await DexFile.create(inputFilePath);
		if(fileMeta)
			twigDiskFile.meta = fileMeta;

		if(op==="dexid")
		{
			r = await identify(twigDiskFile, {xlog});
		}
		else if(op==="dexvert")
		{
			const dexState = await dexvert(twigDiskFile, await DexFile.create(outputDirPath), {xlog, ...dexvertOptions});
			r = dexState ? {json : dexState.serialize(), pretty : dexState.pretty()} : `dexvert failed to return a dexState object for inputFilePath ${inputFilePath} and outputDirPath ${outputDirPath}`;
		}
	}
	catch(err)
	{
		r ||= err.stack;
	}

	return {[typeof r==="string" ? "err" : "r"] : r};
}, () => Array.from(logLines));
