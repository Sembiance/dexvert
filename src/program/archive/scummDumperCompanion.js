import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";
import {punycode} from "thirdParty";

const progBasePath = Program.binPath("scummDumperCompanion");

export class scummDumperCompanion extends Program
{
	website    = "https://raw.githubusercontent.com/scummvm/scummvm/master/devtools/dumper-companion.py";
	bin        = path.join(progBasePath, "env/bin/python3");
	args       = r => [path.join(progBasePath, "dumper-companion.py"), "iso", r.inFile(), r.outDir()];	// note: data-fork only files are not wrapped in MacBinary, thus type/creator is lost. Can add --forcemacbinary if I want to preserve it
	runOptions = {env : {VIRTUAL_ENV : path.join(progBasePath, "env")}};
	postExec   = async r =>
	{
		// usually there is just a single 'hfs' subdir, so move everything up 1 level
		const outDirPath = r.outDir({absolute : true});
		const outDirs = await fileUtil.tree(outDirPath, {nofile : true, depth : 1});
		if(outDirs.length===1)
		{
			// rename the hfs dir to a temp name just to avoid collisions
			const tmpDirPath = await fileUtil.genTempPath(outDirPath);
			await Deno.rename(outDirs[0], tmpDirPath);

			const subFiles = await fileUtil.tree(tmpDirPath, {depth : 1});
			await subFiles.parallelMap(subFile => Deno.rename(subFile, path.join(outDirPath, path.basename(subFile))));
		}

		// now we need to rename any files that start with 'xn--' to their proper names. Note that the script does some special escaping for characters
		const unescapeString = s =>
		{
			let origName = "";
			let i = 0;
			while(i<s.length)
			{
				const hi = s.charCodeAt(i);
				if(hi===0x81)
				{
					i++;
					if(i>=s.length)
						throw new Error("Error decoding string");
					
					const low = s.charCodeAt(i);
					origName += low===0x79 ? String.fromCharCode(0x81) : String.fromCharCode(low - 0x80);
				}
				else
				{
					origName += String.fromCharCode(hi);
				}
				i++;
			}
			return origName;
		};

		for(const filePath of (await fileUtil.tree(r.outDir({absolute : true}))).sortMulti([o => o.split("/").length], [true]))
		{
			if(!path.basename(filePath).startsWith("xn--"))
				continue;

			await Deno.rename(filePath, path.join(path.dirname(filePath), unescapeString(punycode.decode(path.basename(filePath).substring(4))).toVisible().replaceAll("/", "⁄")));
		}
	};
	renameOut  = false;
}
