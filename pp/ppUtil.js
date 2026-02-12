import {xu} from "xu";
import {path, getAvailablePort} from "std";
import {runUtil, fileUtil} from "xutil";
import {C} from "../src/C.js";

const ALLOWED_PP_ERRORS =
[
	/RetryError: Retrying exceeded the maxAttempts/,
	/Failed to decode text file of.*buffer exceeds maximum length$/,
	/No match for.* font-family./,
	"a non-XML character",
	"an unknown namespace prefix",
	"BackgroundImage filter input isn't supported and not planed",
	"cache resources exhausted",
	`Cairo error "out of memory"`,
	"convert: no images defined",
	"does not contain any stream and original exists true",
	"failed to allocate an image",
	"ffmpeg failed to resample the input audio file",
	"identify: improper image header",
	"IEND: CRC error",
	"improper image header",
	"insufficient image data in file",
	"InstExpl.wcx",
	"Invalid data found when processing input",
	"invalid colormap index",
	"invalid matrix (not invertible)",
	"InvalidStateError: readyState not OPEN",
	"moov atom not found",
	"negative or zero image size",
	"Not a JPEG file: starts with",
	"output dimensions must be positive",
	"Output file #0 does not contain any stream",	// happens if an MP4 video only has an audio stream: https://discmaster.textfiles.com/browse/17034/Sybex_Virtual_Trainer_CCNP_Switching.iso/ccnp2711/media/content/graphics/animations/0104_sounds/11.swf
	"provided data has not an UTF-8 encoding",
	"SVG data parsing failed cause an unknown namespace prefix",
	"SVG data parsing failed cause nodes limit reached",
	"SVG data parsing failed cause the document does not have a root node",
	"SVG has an invalid size",
	"The best audio stream is unknown",
	"unknown entity reference '"
];
export {ALLOWED_PP_ERRORS};

export function isFileBlocked(item, fileid)
{
	return fileid?.length && (item?.blocks || []).some(({block}) => block.startsWith(fileid) || fileid.startsWith(block));
}

export async function classify({taskRunner, xlog, filesToProcess, itemClassifyDirPath, filesDirPath, type, libraries, preProcess, preProcessSuffix, processor, batchSize, filesAtOnce=10, startTimeout=xu.MINUTE*5, processTimeout=xu.MINUTE*10})
{
	const cwd = path.join(import.meta.dirname, type);
	const env = {
		VIRTUAL_ENV     : path.join(cwd, "env"),
		HOME            : path.join(cwd, "home"),
		LD_LIBRARY_PATH : libraries.map(v => path.join(cwd, "env", "lib", "python3.10", "site-packages", v)).join(":"),
		PATH            : `${path.join(cwd, "env", "bin")}:/usr/local/cuda/bin:${Deno.env.get("PATH")}`
	};
	const python3Path = path.join(cwd, "env/bin/python3");

	let typeDirPath = null;
	if(preProcess)
	{
		typeDirPath = path.join(itemClassifyDirPath, type);
		await Deno.mkdir(typeDirPath, {recursive : true});
		for(const o of filesToProcess)
			o.typeFilePath = path.join(typeDirPath, `${path.basename(o.filePath)}${preProcessSuffix || ""}`);

		if(await fileUtil.exists(path.join(cwd, `${type}PreProcess.js`)))
		{
			const runOptions = runUtil.denoRunOpts({cwd});
			if(xlog.atLeast("info"))
				runOptions.stderrcb = line => taskRunner.addError(`${xu.bracket(`PreProcess.js ${type}`)} ${line}`);
			await runUtil.run("deno", runUtil.denoArgs(`${type}PreProcess.js`, filesDirPath, typeDirPath), runOptions);
		}
		else
		{
			taskRunner.startProgress(filesToProcess.length, `Pre-Processing files [${type}]...`);
			const runOptions = {cwd, stdoutcb : () => taskRunner.increment(), env : {...env, CUDA_VISIBLE_DEVICES : "-1"}};
			if(xlog.atLeast("info"))
				runOptions.stderrcb = line => taskRunner.addError(`${xu.bracket(`PreProcess.py ${type}`)} ${line}`);
			await runUtil.run(python3Path, [`${type}PreProcess.py`, filesDirPath, typeDirPath], runOptions);
		}
	}

	taskRunner.startProgress(filesToProcess.length, `Classifying files [${type}]...`);
	await Deno.mkdir(path.join(cwd, "home"), {recursive : true});
	const startServer = async gpuNum =>
	{
		const r = {gpuNum, port : getAvailablePort()};

		const {p, cb} = await runUtil.run(python3Path, [`${type}Server.py`, "--web_port", r.port.toString(), ...(batchSize ? ["--batch_size", batchSize.toString()] : [])], {detached : true, cwd, env : {...env, CUDA_VISIBLE_DEVICES : gpuNum.toString()}});
		r.p = p;
		r.cb = cb;

		if(!(await xu.waitUntil(async () => (await xu.tryFallbackAsync(async () => await xu.fetch(`http://127.0.0.1:${r.port}/status`, {silent : true})))==="a-ok", {timeout : startTimeout})))
		{
			taskRunner.addError(`${type} server failed to start on port ${r.port} within ${startTimeout.msAsHumanReadable({short : true})}. Will try again, so if no more errors, ok to verify.`);
			await runUtil.kill(p);
			await cb();
			return null;
		}

		return r;
	};

	const servers = await [].pushSequence(0, C.CLASSIFY_GPU_COUNT-1).parallelMap(async gpuNum =>
	{
		let server = null;
		await xu.waitUntil(async () => { server = await startServer(gpuNum); return !!server; });
		return server;
	});

	const serverRestartCounts = {};

	const restartServer = async server =>
	{
		await runUtil.kill(server.p);
		await server.cb();

		serverRestartCounts[server.gpuNum] ||= 0;
		serverRestartCounts[server.gpuNum]++;
		if(serverRestartCounts[server.gpuNum]>3)
		{
			console.error(`${type} server on GPU ${server.gpuNum} has failed to restart ${serverRestartCounts[server.gpuNum]} times, giving up!\nWARNING! batch will be SKIPPED!`);
			return false;
		}

		Object.assign(server, await startServer(server.gpuNum));
		return true;
	};

	const availableServers = Array.from(servers);
	const fileBatches = filesToProcess.chunk(filesAtOnce);

	const processBatch = async (server, fileBatch) =>
	{
		const serverStatus = await xu.fetch(`http://127.0.0.1:${server.port}/status`, {timeout : xu.SECOND*5});
		if(serverStatus!=="a-ok")
		{
			taskRunner.addError(`${type} server failed a status check with status ${serverStatus} (restarting ${type} server, if no more errors appear, ok to accept results)`);
			await restartServer(server);
		}

		const results = await xu.fetch(`http://127.0.0.1:${server.port}/process`, {timeout : processTimeout, asJSON : true, json : {filePaths : fileBatch.map(o => o[preProcess ? "typeFilePath" : "filePath"])}});
		if(results?.length!==fileBatch.length)
		{
			taskRunner.addError(`${type} results length mismatch! ${results?.length} vs ${fileBatch.length}`, true);
			if(!(await restartServer(server)))
				return true;	// if we've restarted the server too many times, it'll return false, in which case we should return true which wil abandon this batch
			return false;
		}

		taskRunner.incrementBy(fileBatch?.length || 0);
		await processor(fileBatch, results);
		availableServers.push(server);
		return true;
	};

	while(fileBatches.length)
	{
		let availableServer = null;
		await xu.waitUntil(() => { availableServer = availableServers.shift(); return !!availableServer; });
		const fileBatch = fileBatches.pop();
		if(!fileBatch?.length)
		{
			availableServers.push(availableServer);
			continue;
		}

		xu.waitUntil(async () => await processBatch(availableServer, fileBatch));
	}

	await xu.waitUntil(() => availableServers.length===servers.length);	// wait for batches to finish

	await servers.parallelMap(async ({p, cb}) =>
	{
		await runUtil.kill(p);
		await cb();
	});

	if(typeDirPath)
		await fileUtil.unlink(typeDirPath, {recursive : true});
}

