import {xu} from "xu";
import {xwork} from "xwork";
import {dexvert} from "../src/dexvert.js";
import {XLog} from "xlog";
import {DexFile} from "../src/DexFile.js";

const MAX_DEXVERT_DURATION = xu.MINUTE*30;

await xwork.openConnection();

await xwork.recv(async ({sampleFilePath, tmpOutDirPath, logFilePath, asFormat, programFlag}) =>
{
	let tooLongTimer = null;
	try
	{
		tooLongTimer = setTimeout(async () =>
		{
			tooLongTimer = null;
			await xwork.send({sampleFilePath, err : `Took too long to process and was aborted.`});
			xwork.recvAbort();
		}, MAX_DEXVERT_DURATION);	// for some extensions (like macromedia directory, allow a much longer duration timeframe)

		const xlog = new XLog("debug", {logFilePath});
		const dexvertOpts = {xlog, programFlag};
		if(asFormat)
			dexvertOpts.asFormat = asFormat;

		const dexState = await dexvert(await DexFile.create(sampleFilePath), await DexFile.create(tmpOutDirPath), dexvertOpts);
		if(tooLongTimer===null)
			return console.error(`Sample ${sampleFilePath} was cancelled due to taking too long but finished anyways, taking ${dexState?.duration?.msAsHumanReadable({short : true})} and was handled as ${dexState?.phase?.id?.family}/${dexState?.phase?.id?.formatid}`);

		clearTimeout(tooLongTimer);
		if(!dexState)
			return await xwork.send({sampleFilePath, err : "No dexState returned!"});

		await xwork.send({sampleFilePath, tmpOutDirPath, dexData : dexState.serialize()});
	}
	catch(err)
	{
		if(tooLongTimer!==null)
			await xwork.send({sampleFilePath, err : `dexvert failed (with error: ${err.stack}`});
	}
});

await xwork.closeConnection();
Deno.exit();
