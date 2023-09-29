import {xu} from "xu";
import {xwork} from "xwork";
import {dexvert} from "../dexvert.js";
import {identify} from "../identify.js";
import {XLog} from "xlog";
import {DexFile} from "../DexFile.js";
import {init as initPrograms, monitor as monitorPrograms} from "../program/programs.js";
import {init as initFormats, monitor as monitorFormats} from "../format/formats.js";

const DEX_MAX_DURATION = xu.HOUR;
const DEX_LONG_DURATION_EXTS = [".dir", ".dxr", ".drx", ".cxt", ".cst", ".dcr", ".hlp", ".rsrc"];

await initPrograms();
await initFormats();

await monitorFormats();
await monitorPrograms();

await xwork.openConnection();

await xwork.recv(async ({rpcid, inputFilePath, outputDirPath, prod, logLevel="error", fileMeta, op, dexverOptions={}}) =>
{
	const logLines = [];
	const xlogOptions = {};
	if(prod)
		xlogOptions.logger = v => logLines.push(v);
	const xlog = new XLog(logLevel, xlogOptions);

	let tooLongTimer = null;
	try
	{
		const twigDiskFile = await DexFile.create(inputFilePath);
		if(fileMeta)
			twigDiskFile.meta = fileMeta;

		tooLongTimer = setTimeout(async () =>
		{
			tooLongTimer = null;
			await xwork.send({rpcid, logLines, err : `${op} Took too long to process and was aborted.`});
			xwork.recvAbort();
		}, DEX_MAX_DURATION*(DEX_LONG_DURATION_EXTS.some(ext => inputFilePath.toLowerCase().endsWith(ext)) ? 2 : 1));	// for some extensions (like macromedia directory, allow a much longer duration timeframe)

		let r = null;
		if(op==="dexid")
		{
			r = await identify(twigDiskFile, {xlog});
		}
		else if(op==="dexvert")
		{
			const dexState = await dexvert(twigDiskFile, await DexFile.create(outputDirPath), {xlog, ...dexverOptions});
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
