import {xu} from "xu";
import {xwork} from "xwork";
import {dexvert} from "../dexvert.js";
import {fileUtil} from "xutil";
import {XLog} from "xlog";
import {DexFile} from "../DexFile.js";

const MAX_DEXVERT_DURATION = xu.HOUR;

await xwork.openConnection();

await xwork.recv(async ({inputFilePath, outDirPath, jsonFilePath, fileMeta, programFlag={}}) =>
{
	let tooLongTimer = null;
	try
	{
		await Deno.mkdir(outDirPath, {recursive : true});

		const inputFile = await DexFile.create(inputFilePath);
		if(fileMeta)
			inputFile.meta = fileMeta;

		tooLongTimer = setTimeout(async () =>
		{
			tooLongTimer = null;
			await xwork.send({inputFilePath, err : `Took too long to process and was aborted.`});
			xwork.recvAbort();
		}, MAX_DEXVERT_DURATION);

		const dexState = await dexvert(inputFile, await DexFile.create(outDirPath), {xlog : new XLog("error"), programFlag});
		if(tooLongTimer===null)
			return console.error(`Sample ${inputFilePath} was cancelled due to taking too long but finished anyways, taking ${dexState?.duration?.msAsHumanReadable({short : true})} and was handled as ${dexState?.phase?.id?.family}/${dexState?.phase?.id?.formatid}`);

		clearTimeout(tooLongTimer);
		tooLongTimer = null;
		if(!dexState)
			return await xwork.send({inputFilePath, err : "No dexState returned!"});

		const dexData = dexState.serialize();
		if(jsonFilePath)
			await fileUtil.writeTextFile(jsonFilePath, JSON.stringify(dexData));

		await xwork.send({inputFilePath, done : true, createdFiles : (dexData.created?.files?.output || []), fileMeta : (dexData?.phase?.meta?.fileMeta || {})});
	}
	catch(err)
	{
		if(tooLongTimer!==null)
			await xwork.send({inputFilePath, err : `dexvert failed (with error: ${err.stack}`});
	}
});

await xwork.closeConnection();
Deno.exit();
