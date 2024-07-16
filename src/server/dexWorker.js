import {xu} from "xu";
import {xwork} from "xwork";
import {dexvert} from "../dexvert.js";
import {identify} from "../identify.js";
import {XLog} from "xlog";
import {path} from "std";
import {DexFile} from "../DexFile.js";
import {init as initPrograms, programChanged} from "../program/programs.js";
import {init as initFormats, formatChanged, formats} from "../format/formats.js";

await initPrograms();
await initFormats();

const slowExtensions = Object.values(formats).filter(format => format.slow && format.ext?.length).flatMap(format => format.ext).unique();

await xwork.openConnection();

await xwork.recv(async ({rpcid, inputFilePath, outputDirPath, logLevel="error", fileMeta, op, change={}, timeout, dexvertOptions={}}) =>
{
	if(op==="formatChange")
		return await formatChanged(change);
	if(op==="programChange")
		return await programChanged(change);
	
	timeout ||= xu.HOUR*(slowExtensions.includes(path.extname(inputFilePath)?.toLowerCase()) ? 4 : 1.5);	// for slow formats, if we match the extension, give a little more time

	const logLines = [];
	const xlogOptions = {};
	xlogOptions.logger = v => logLines.push(v);
	const xlog = new XLog(logLevel, xlogOptions);
	if(xlog.atLeast("debug"))
		xlog.alwaysEcho = true;

	let tooLongTimer = null;
	try
	{
		const twigDiskFile = await DexFile.create(inputFilePath);
		if(fileMeta)
			twigDiskFile.meta = fileMeta;

		tooLongTimer = setTimeout(async () =>
		{
			tooLongTimer = null;
			await xwork.send({rpcid, logLines, timedout : true, err : `${op} Took too long to process and was aborted for inputFilePath ${inputFilePath} and outputDirPath ${outputDirPath}`});
			xwork.recvAbort();
		}, timeout);

		let r = null;
		if(op==="dexid")
		{
			r = await identify(twigDiskFile, {xlog});
		}
		else if(op==="dexvert")
		{
			const dexState = await dexvert(twigDiskFile, await DexFile.create(outputDirPath), {xlog, ...dexvertOptions});
			if(dexState)
				r = {json : dexState.serialize(), pretty : dexState.pretty()};
		}
		
		if(tooLongTimer===null)
			return console.error(`${op} twigDiskFilePath ${xu.bracket(inputFilePath)} was cancelled due to taking too long but finished anyways to, taking ${r?.duration?.msAsHumanReadable({short : true})} and was handled as ${r?.phase?.id?.family}/${r?.phase?.id?.formatid}`);
		clearTimeout(tooLongTimer);
		tooLongTimer = null;

		if(!r)
			return await xwork.send({rpcid, logLines, err : `${op} No data returned!`});
		
		await xwork.send({rpcid, logLines, r});
	}
	catch(err)
	{
		console.error(`Error with rpcid ${rpcid}`);
		console.error(err);
		if(tooLongTimer!==null)
			clearTimeout(tooLongTimer);
		await xwork.send({rpcid, logLines, err : `dexvert failed with error: ${err.stack}`});
	}
});

await xwork.closeConnection();
Deno.exit();
