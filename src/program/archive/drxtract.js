import {xu} from "xu";
import {Program} from "../../Program.js";
import {path, base64Decode} from "std";
import {fileUtil} from "xutil";

const progBasePath = Program.binPath("drxtract");

export class drxtract extends Program
{
	website = "https://github.com/System25/drxtract";
	bin     = path.join(progBasePath, "env/bin/drxtract");
	args    = r =>
	{
		const platform = "pc";
		return [platform, r.inFile(), r.outDir()];
	};
	cwd        = () => progBasePath;
	runOptions = {env : {VIRTUAL_ENV : path.join(progBasePath, "env")}};
	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});
		const topLevelFilePaths = await fileUtil.tree(outDirPath, {depth : 1});

		const fields = {};
		const scripts = {};
		const dataFilePaths = await fileUtil.tree(outDirPath, {nodir : true, regex : /cas\/\d+\/data\.json/});
		for(const dataFilePath of dataFilePaths)
		{
			const data = xu.parseJSON(await fileUtil.readTextFile(dataFilePath));
			if(!data)
			{
				r.xlog.warn`Failed to parse data.json file: ${dataFilePath}`;
				continue;
			}

			const castid = path.basename(path.dirname(dataFilePath));
			const destFilenamePrefix = `${castid.padStart(5, "0")}_${data.type}`;

			const handleCastFiles = async (regs, once=true) =>
			{
				const castFilePaths = await fileUtil.tree(path.dirname(dataFilePath), {depth : 1, nodir : true});
				let foundOne = false;
				for(const reg of regs)
				{
					if(once && foundOne)
						break;

					for(const castFilePath of castFilePaths)
					{
						if(!reg.test(castFilePath))
							continue;
						
						foundOne = true;
						await fileUtil.move(castFilePath, path.join(outDirPath, `${destFilenamePrefix}_${data.name ? `${data.name}_${path.basename(castFilePath)}` : path.basename(castFilePath)}`));
					}
				}
			};

			if(data.type==="bitmap")	// eslint-disable-line unicorn/prefer-switch
			{
				await handleCastFiles([/\d+\.png$/i, /\d+\.bmp$/i]);
			}
			else if(data.type==="sound")
			{
				await handleCastFiles([/\d+\.wav$/i, /\d+\.mp3$/i]);
			}
			else if(data.type==="script")
			{
				scripts[castid] = `-- ${destFilenamePrefix}\n${new TextDecoder().decode(base64Decode(data.code))}`;
			}
			else if(data.type==="field")
			{
				// logic from: https://github.com/scummvm/scummvm/blob/master/engines/director/stxt.cpp
				const stxtFilepaths = await fileUtil.tree(path.dirname(dataFilePath), {regex : /\.STXT$/, depth : 1, nodir : true});
				for(const stxtFilepath of stxtFilepaths)
				{
					const stxtData = await Deno.readFile(stxtFilepath);
					fields[castid] = `${destFilenamePrefix}_${path.basename(stxtFilepath, ".STXT")}: ${stxtData.getString(12, stxtData.getUInt32BE(4))}`;
				}
			}
			else
			{
				r.xlog.warn`Unhandled type ${data.type} in data.json file ${path.relative(outDirPath, dataFilePath)} with data: ${data}`;
			}
		}

		for(const [name, o] of [["scripts", scripts], ["fields", fields]])
		{
			if(Object.keys(o).length)
				await fileUtil.writeTextFile(path.join(outDirPath, `${name}.txt`), Object.entries(o).sortMulti([([castid]) => +castid]).map(([, v]) => v).join("\n"));
		}

		// remove our original output files
		for(const topLevelFilePath of topLevelFilePaths)
			await fileUtil.unlink(topLevelFilePath, {recursive : true});
	};
	renameOut  = false;
}
